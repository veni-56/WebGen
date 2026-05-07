"""
optimize.py — Static site optimization pipeline.

Provides:
  optimize_dir(out_dir, version_tag)
    - Minify HTML, CSS, JS
    - Inline critical CSS
    - Add lazy loading to images
    - Defer non-critical scripts
    - Version asset filenames (style.css -> style.v<tag>.css)
    - Gzip compress all text assets

  optimize_image(src_path, dest_dir)
    - Generate thumbnail (150px), medium (600px), original
    - Returns dict of {size: path}

All functions are pure (no Flask imports) so they can run in the build thread.
"""
import gzip, hashlib, io, os, re, shutil
from pathlib import Path

# Optional heavy deps — gracefully degrade if missing
try:
    from PIL import Image as _PIL
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

# ─────────────────────────────────────────────────────────────────────────────
# 1. Minifiers (stdlib-only, no external tools required)
# ─────────────────────────────────────────────────────────────────────────────

def minify_html(html: str) -> str:
    """
    Lightweight HTML minifier:
    - Collapse whitespace between tags
    - Remove HTML comments (but keep IE conditionals and SSI)
    - Strip leading/trailing whitespace from lines
    """
    # Remove HTML comments except <!--[if ...]> and <!-- # -->
    html = re.sub(r'<!--(?!\[if)(?!#).*?-->', '', html, flags=re.DOTALL)
    # Collapse runs of whitespace between tags to a single space
    html = re.sub(r'>\s{2,}<', '> <', html)
    # Strip leading/trailing whitespace per line
    lines = [l.strip() for l in html.splitlines()]
    html  = '\n'.join(l for l in lines if l)
    return html


def minify_css(css: str) -> str:
    """
    Lightweight CSS minifier:
    - Remove comments
    - Collapse whitespace
    - Remove unnecessary semicolons and spaces around : ; { }
    """
    # Remove /* ... */ comments
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    # Collapse whitespace
    css = re.sub(r'\s+', ' ', css)
    # Remove spaces around structural characters
    css = re.sub(r'\s*([{};:,>~+])\s*', r'\1', css)
    # Remove trailing semicolon before }
    css = css.replace(';}', '}')
    return css.strip()


def minify_js(js: str) -> str:
    """
    Very conservative JS minifier (no AST — safe for any JS):
    - Remove single-line comments (// ...) not inside strings
    - Collapse blank lines
    - Strip leading/trailing whitespace per line
    Does NOT remove multi-line comments or rename variables.
    """
    lines = []
    for line in js.splitlines():
        stripped = line.strip()
        # Remove pure comment lines
        if stripped.startswith('//'):
            continue
        lines.append(stripped)
    # Collapse multiple blank lines to one
    result = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines))
    return result.strip()


# ─────────────────────────────────────────────────────────────────────────────
# 2. Critical CSS inlining
# ─────────────────────────────────────────────────────────────────────────────

# Selectors that are "above the fold" — body, html, nav, header, hero, h1-h3
_CRITICAL_SELECTORS = re.compile(
    r'(html|body|nav|header|\.hero|\.navbar|h1|h2|h3|\.cta|\.banner)[^{]*\{[^}]*\}',
    re.IGNORECASE
)

def extract_critical_css(css: str) -> str:
    """Extract rules likely needed for above-the-fold rendering."""
    # Also include :root (CSS variables) and @font-face
    root_rules  = re.findall(r':root\s*\{[^}]*\}', css, re.DOTALL)
    font_rules  = re.findall(r'@font-face\s*\{[^}]*\}', css, re.DOTALL)
    crit_rules  = _CRITICAL_SELECTORS.findall(css)
    parts = root_rules + font_rules + crit_rules
    return minify_css('\n'.join(parts))


def inline_critical_css(html: str, css: str) -> str:
    """
    Inject critical CSS as <style> in <head>, and convert the main
    <link rel="stylesheet"> to load asynchronously (non-render-blocking).
    """
    critical = extract_critical_css(css)
    if not critical:
        return html

    critical_tag = f'<style id="wbs-critical">{critical}</style>'

    # Replace <link rel="stylesheet" href="style.css"> with async load + noscript fallback
    async_link = (
        '<link rel="preload" href="style.css" as="style" '
        'onload="this.onload=null;this.rel=\'stylesheet\'">'
        '<noscript><link rel="stylesheet" href="style.css"></noscript>'
    )
    html = re.sub(
        r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']style\.css["\'][^>]*>',
        async_link,
        html,
        flags=re.IGNORECASE
    )
    # Also handle reversed attribute order
    html = re.sub(
        r'<link[^>]+href=["\']style\.css["\'][^>]*rel=["\']stylesheet["\'][^>]*>',
        async_link,
        html,
        flags=re.IGNORECASE
    )

    # Inject critical CSS just before </head>
    html = html.replace('</head>', critical_tag + '\n</head>', 1)
    return html


# ─────────────────────────────────────────────────────────────────────────────
# 3. Lazy loading + script deferral
# ─────────────────────────────────────────────────────────────────────────────

def add_lazy_loading(html: str) -> str:
    """Add loading="lazy" to <img> tags that don't already have it."""
    def _patch_img(m):
        tag = m.group(0)
        if 'loading=' in tag:
            return tag
        # Insert loading="lazy" before the closing >
        return tag[:-1] + ' loading="lazy">'
    return re.sub(r'<img\b[^>]*>', _patch_img, html, flags=re.IGNORECASE)


def defer_scripts(html: str) -> str:
    """
    Add defer to <script src="..."> tags that don't have async/defer.
    Skips inline scripts and scripts already marked async/defer.
    """
    def _patch_script(m):
        tag = m.group(0)
        if 'defer' in tag or 'async' in tag or 'src=' not in tag:
            return tag
        return tag.replace('<script ', '<script defer ', 1)
    return re.sub(r'<script\b[^>]*>', _patch_script, html, flags=re.IGNORECASE)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Asset versioning
# ─────────────────────────────────────────────────────────────────────────────

def version_assets(html: str, css_hash: str, js_hash: str) -> str:
    """
    Replace style.css → style.css?v=<hash> and script.js → script.js?v=<hash>
    in HTML. Uses query-string versioning (no file rename needed).
    """
    html = re.sub(
        r'(href=["\'])style\.css(["\'])',
        rf'\1style.css?v={css_hash}\2',
        html, flags=re.IGNORECASE
    )
    html = re.sub(
        r'(src=["\'])script\.js(["\'])',
        rf'\1script.js?v={js_hash}\2',
        html, flags=re.IGNORECASE
    )
    return html


def _file_hash(path: Path) -> str:
    if not path.exists():
        return 'x'
    return hashlib.md5(path.read_bytes()).hexdigest()[:8]


# ─────────────────────────────────────────────────────────────────────────────
# 5. Gzip compression
# ─────────────────────────────────────────────────────────────────────────────

def gzip_file(path: Path) -> Path:
    """Write a .gz companion file next to path. Returns the .gz path."""
    gz_path = path.with_suffix(path.suffix + '.gz')
    with open(path, 'rb') as f_in, gzip.open(gz_path, 'wb', compresslevel=9) as f_out:
        shutil.copyfileobj(f_in, f_out)
    return gz_path


# ─────────────────────────────────────────────────────────────────────────────
# 6. Main pipeline: optimize_dir
# ─────────────────────────────────────────────────────────────────────────────

def optimize_dir(out_dir: Path) -> dict:
    """
    Run the full optimization pipeline on a built site directory.
    Modifies files in-place. Returns stats dict.
    """
    out_dir = Path(out_dir)
    stats   = {
        'html_files': 0, 'css_saved': 0, 'js_saved': 0,
        'gz_files': 0, 'errors': []
    }

    # 1. Minify + version CSS
    css_path = out_dir / 'style.css'
    css_hash = _file_hash(css_path)
    if css_path.exists():
        try:
            raw = css_path.read_text(encoding='utf-8')
            minified = minify_css(raw)
            stats['css_saved'] = len(raw) - len(minified)
            css_path.write_text(minified, encoding='utf-8')
            gzip_file(css_path)
            stats['gz_files'] += 1
        except Exception as e:
            stats['errors'].append(f'CSS: {e}')

    # 2. Minify + version JS
    js_path = out_dir / 'script.js'
    js_hash = _file_hash(js_path)
    if js_path.exists():
        try:
            raw = js_path.read_text(encoding='utf-8')
            minified = minify_js(raw)
            stats['js_saved'] = len(raw) - len(minified)
            js_path.write_text(minified, encoding='utf-8')
            gzip_file(js_path)
            stats['gz_files'] += 1
        except Exception as e:
            stats['errors'].append(f'JS: {e}')

    # 3. Process each HTML file
    css_content = css_path.read_text(encoding='utf-8') if css_path.exists() else ''
    for html_file in out_dir.glob('*.html'):
        try:
            html = html_file.read_text(encoding='utf-8')
            html = inline_critical_css(html, css_content)
            html = add_lazy_loading(html)
            html = defer_scripts(html)
            html = version_assets(html, css_hash, js_hash)
            html = minify_html(html)
            html_file.write_text(html, encoding='utf-8')
            gzip_file(html_file)
            stats['html_files'] += 1
            stats['gz_files']   += 1
        except Exception as e:
            stats['errors'].append(f'{html_file.name}: {e}')

    return stats


# ─────────────────────────────────────────────────────────────────────────────
# 7. Image optimization
# ─────────────────────────────────────────────────────────────────────────────

IMAGE_SIZES = {
    'thumb':    150,   # px (longest side)
    'medium':   600,
    'original': None,  # no resize
}

def optimize_image(src_path: Path, dest_dir: Path) -> dict:
    """
    Generate thumbnail, medium, and original variants of an image.
    Returns { 'thumb': path, 'medium': path, 'original': path }.
    Falls back to copying the original if Pillow is not installed.
    """
    src_path  = Path(src_path)
    dest_dir  = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    stem      = src_path.stem
    suffix    = src_path.suffix.lower()
    result    = {}

    if not _HAS_PIL:
        # No Pillow — just copy original
        dest = dest_dir / src_path.name
        shutil.copy2(src_path, dest)
        result = {'thumb': str(dest), 'medium': str(dest), 'original': str(dest)}
        return result

    try:
        img = _PIL.open(src_path).convert('RGBA' if suffix == '.png' else 'RGB')
    except Exception:
        shutil.copy2(src_path, dest_dir / src_path.name)
        return {'thumb': str(dest_dir / src_path.name),
                'medium': str(dest_dir / src_path.name),
                'original': str(dest_dir / src_path.name)}

    save_fmt = 'PNG' if suffix == '.png' else 'JPEG'
    save_kw  = {'optimize': True} if save_fmt == 'JPEG' else {}
    if save_fmt == 'JPEG':
        save_kw['quality'] = 82
        img = img.convert('RGB')

    for size_name, max_px in IMAGE_SIZES.items():
        out_name = f'{stem}_{size_name}{suffix}'
        out_path = dest_dir / out_name
        if max_px is None:
            variant = img.copy()
        else:
            variant = img.copy()
            variant.thumbnail((max_px, max_px), _PIL.LANCZOS)
        variant.save(str(out_path), save_fmt, **save_kw)
        result[size_name] = str(out_path)

    return result
