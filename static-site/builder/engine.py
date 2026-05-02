"""
engine.py — Template Engine for Website Builder System

Syntax supported in .html template files:
  {{key}}                    — simple value substitution
  {{#each items}}...{{/each}} — loop over a list
  {{#if feature}}...{{/if}}  — conditional block
  {{>partial_name}}          — include another template
"""

import re
from pathlib import Path
from typing import Any

TEMPLATES_DIR = Path(__file__).parent / "templates"


# ── 1. Template loader ────────────────────────────────────────────────────────

def load_template(name: str) -> str:
    """Load a template file by name (with or without .html extension)."""
    if not name.endswith(".html"):
        name += ".html"
    path = TEMPLATES_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path.read_text(encoding="utf-8")


# ── 2. Core renderer ──────────────────────────────────────────────────────────

def render(template: str, ctx: dict) -> str:
    """
    Render a template string with the given context dict.
    Processes in order: partials → conditionals → loops → variables.
    """
    template = _process_partials(template, ctx)
    template = _process_conditionals(template, ctx)
    template = _process_loops(template, ctx)
    template = _process_variables(template, ctx)
    return template


def render_file(name: str, ctx: dict) -> str:
    """Load a template file and render it."""
    return render(load_template(name), ctx)


# ── 3. Partials  {{>partial_name}} ───────────────────────────────────────────

def _process_partials(template: str, ctx: dict) -> str:
    def replacer(m):
        partial_name = m.group(1).strip()
        try:
            partial_src = load_template(partial_name)
            return render(partial_src, ctx)   # recursive render
        except FileNotFoundError:
            return f"<!-- partial '{partial_name}' not found -->"
    return re.sub(r'\{\{>\s*(\w+)\s*\}\}', replacer, template)


# ── 4. Conditionals  {{#if key}}...{{/if}} ───────────────────────────────────

def _process_conditionals(template: str, ctx: dict) -> str:
    # {{#if key}}...{{else}}...{{/if}}  (else is optional)
    pattern = re.compile(
        r'\{\{#if\s+(\S+?)\s*\}\}(.*?)(?:\{\{else\}\}(.*?))?\{\{/if\}\}',
        re.DOTALL
    )
    def replacer(m):
        key      = m.group(1)
        if_body  = m.group(2) or ""
        else_body= m.group(3) or ""
        value    = _resolve(key, ctx)
        return if_body if value else else_body
    return pattern.sub(replacer, template)


# ── 5. Loops  {{#each items}}...{{/each}} ────────────────────────────────────

def _process_loops(template: str, ctx: dict) -> str:
    pattern = re.compile(
        r'\{\{#each\s+(\S+?)\s*\}\}(.*?)\{\{/each\}\}',
        re.DOTALL
    )
    def replacer(m):
        key      = m.group(1)
        body     = m.group(2)
        items    = _resolve(key, ctx)
        if not items or not isinstance(items, (list, tuple)):
            return ""
        parts = []
        for i, item in enumerate(items):
            # Build item context: item fields + loop meta
            item_ctx = dict(ctx)
            if isinstance(item, dict):
                item_ctx.update(item)
            else:
                item_ctx["this"] = item
            item_ctx["@index"]  = i
            item_ctx["@first"]  = (i == 0)
            item_ctx["@last"]   = (i == len(items) - 1)
            item_ctx["@length"] = len(items)
            parts.append(render(body, item_ctx))
        return "".join(parts)
    return pattern.sub(replacer, template)


# ── 6. Variables  {{key}} ────────────────────────────────────────────────────

def _process_variables(template: str, ctx: dict) -> str:
    def replacer(m):
        key = m.group(1).strip()
        val = _resolve(key, ctx)
        if val is None:
            return m.group(0)   # leave unreplaced if not found
        return str(val)
    return re.sub(r'\{\{([^#/>{][^}]*?)\}\}', replacer, template)


# ── 7. Key resolver (supports dot notation: features.dark_mode) ──────────────

def _resolve(key: str, ctx: dict) -> Any:
    parts = key.split(".")
    val   = ctx
    for part in parts:
        if isinstance(val, dict):
            val = val.get(part)
        else:
            return None
        if val is None:
            return None
    return val


# ── 8. Context builder ────────────────────────────────────────────────────────

def build_context(cfg: dict, page_key: str = "", extra: dict | None = None) -> dict:
    """
    Build a flat rendering context from config.
    Merges top-level config, features, content, and page-specific data.
    """
    name = cfg["site_name"]
    ctx  = {
        # Top-level
        "site_name":       name,
        "site_initial":    name[0].upper(),
        "site_name_lower": name.lower().replace(" ", ""),
        "tagline":         cfg.get("tagline", ""),
        "description":     cfg.get("description", ""),
        "cta_text":        cfg.get("cta_text", "Get Started"),
        "cta_link":        cfg.get("cta_link", "contact.html"),
        "primary_color":   cfg["primary_color"],
        "secondary_color": cfg["secondary_color"],
        "font":            cfg.get("font", "Inter"),
        "font_url":        cfg.get("font", "Inter").replace(" ", "+"),
        "year":            "2025",
        "page_key":        page_key,

        # Feature flags (accessible as features.dark_mode etc.)
        "features":        cfg.get("features", {}),

        # Content arrays
        **cfg.get("content", {}),
    }

    # Flatten features for direct access: dark_mode, animations, etc.
    for k, v in cfg.get("features", {}).items():
        ctx[k] = v

    # Page-specific
    pages = cfg.get("pages", {})
    if page_key and page_key in pages:
        page_cfg = pages[page_key]
        ctx["page_title"]    = page_cfg.get("title", page_key.title())
        ctx["page_sections"] = page_cfg.get("sections", [])

    # Nav links (for navbar template)
    nav_links = []
    for pk, pcfg in pages.items():
        nav_links.append({
            "key":    pk,
            "label":  pcfg.get("title", pk.title()),
            "href":   pcfg.get("file", pk + ".html"),
            "active": pk == page_key,
        })
    ctx["nav_links"] = nav_links

    if extra:
        ctx.update(extra)

    return ctx
