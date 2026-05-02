import pathlib, sys

WG = pathlib.Path("website-generator")

def read_body(f):
    return (WG / f).read_text(encoding="utf-8")

# Read all body files
index_body     = read_body("_index_body.html")
about_body     = read_body("_about_body.html")
services_body  = read_body("_services_body.html")
portfolio_body = read_body("_portfolio_body.html")
blog_body      = read_body("_blog_body.html")
contact_body   = read_body("_contact_body.html")
pricing_body   = read_body("_pricing_body.html")
team_body      = read_body("_team_body.html")
faq_body       = read_body("_faq_body.html")
testimonials_body = read_body("_testimonials_body.html")

# Build the CSS
css_content = """:root { --primary: PRIMARY_COLOR; --secondary: SECONDARY_COLOR; }
.reveal { opacity: 0; transform: translateY(20px); transition: opacity .6s ease, transform .6s ease; }
.reveal.visible { opacity: 1; transform: none; }
[x-cloak] { display: none !important; }
.active-link { color: PRIMARY_COLOR !important; border-bottom: 2px solid PRIMARY_COLOR; }
.toast { position: fixed; bottom: 2rem; right: 2rem; background: #166534; color: #bbf7d0; padding: 1rem 1.5rem; border-radius: 10px; font-size: .9rem; font-weight: 500; box-shadow: 0 8px 24px rgba(0,0,0,.3); transform: translateY(100px); opacity: 0; transition: all .4s ease; z-index: 9999; }
.toast.show { transform: translateY(0); opacity: 1; }
.c-kw { color: #79b8ff; } .c-fn { color: #b392f0; } .c-str { color: #9ecbff; } .c-num { color: #f97583; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
.float-anim { animation: float 3s ease-in-out infinite; }
.float-anim-delay { animation: float 3s ease-in-out infinite; animation-delay: .8s; }
.portfolio-hidden { display: none !important; }
"""

# Build the JS
js_content = """// Active nav link detection
(function () {
  const page = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('a[data-nav]').forEach(a => {
    const href = a.getAttribute('href');
    if (href === page || (page === '' && href === 'index.html')) {
      a.classList.add('active-link');
    }
  });
})();

// Scroll reveal
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); revealObserver.unobserve(e.target); } });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

// Counter animation
function animateCounter(el) {
  const target = parseInt(el.dataset.target);
  const suffix = el.dataset.suffix || '';
  let count = 0;
  const step = Math.ceil(target / 60);
  const timer = setInterval(() => { count = Math.min(count + step, target); el.textContent = count.toLocaleString() + suffix; if (count >= target) clearInterval(timer); }, 25);
}
const counterObserver = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.querySelectorAll('[data-target]').forEach(animateCounter); counterObserver.unobserve(e.target); } });
}, { threshold: 0.5 });
document.querySelectorAll('.stats-bar').forEach(el => counterObserver.observe(el));

// Toast notification
function showToast(message) {
  let toast = document.querySelector('.toast');
  if (!toast) { toast = document.createElement('div'); toast.className = 'toast'; document.body.appendChild(toast); }
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 4000);
}

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => { const t = document.querySelector(a.getAttribute('href')); if (t) { e.preventDefault(); t.scrollIntoView({ behavior: 'smooth', block: 'start' }); } });
});

// Navbar scroll shadow
window.addEventListener('scroll', () => {
  const n = document.getElementById('navbar');
  if (n) { n.classList.toggle('shadow-lg', window.scrollY > 10); }
});

// Portfolio filter
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => { b.classList.remove('bg-primary-500','text-white','border-primary-500'); b.classList.add('border-gray-300','dark:border-gray-600','text-gray-600','dark:text-gray-400'); });
    btn.classList.add('bg-primary-500','text-white','border-primary-500');
    btn.classList.remove('border-gray-300','dark:border-gray-600','text-gray-600','dark:text-gray-400');
    const filter = btn.dataset.filter;
    document.querySelectorAll('.portfolio-item').forEach(item => { item.classList.toggle('portfolio-hidden', filter !== 'all' && item.dataset.category !== filter); });
  });
});
"""

# Build the override code
override_lines = [
    "",
    "",
    "# ─────────────────────────────────────────────────────────────────────────────",
    "# STATIC PRO GENERATOR — overrides _gen_static() with Tailwind + Alpine.js",
    "# ─────────────────────────────────────────────────────────────────────────────",
    "",
    "def _sp2_darken(hex_color: str) -> str:",
    '    """Darken a hex color by ~15%."""',
    "    h = hex_color.lstrip('#')",
    "    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)",
    "    return f'#{max(0,int(r*.85)):02x}{max(0,int(g*.85)):02x}{max(0,int(b*.85)):02x}'",
    "",
]

# Write the body constants
bodies = {
    "_SP2_INDEX_BODY":        index_body,
    "_SP2_ABOUT_BODY":        about_body,
    "_SP2_SERVICES_BODY":     services_body,
    "_SP2_PORTFOLIO_BODY":    portfolio_body,
    "_SP2_BLOG_BODY":         blog_body,
    "_SP2_CONTACT_BODY":      contact_body,
    "_SP2_PRICING_BODY":      pricing_body,
    "_SP2_TEAM_BODY":         team_body,
    "_SP2_FAQ_BODY":          faq_body,
    "_SP2_TESTIMONIALS_BODY": testimonials_body,
    "_SP2_CSS":               css_content,
    "_SP2_JS":                js_content,
}

for var_name, content in bodies.items():
    # Escape backslashes and triple-quotes in content
    safe = content.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    override_lines.append(f'{var_name} = """{safe}"""')
    override_lines.append("")

# Write the helper functions and main _gen_static override
override_lines += [
    "",
    "def _sp2_head(name: str, primary: str, secondary: str, font: str, page_title: str) -> str:",
    '    """Generate the HTML head for a Static Pro page."""',
    "    font_url = font.replace(' ', '+')",
    "    dark = _sp2_darken(primary)",
    "    return (",
    '        f\'<!DOCTYPE html>\\n\'',
    '        f\'<html lang="en" x-data="{{ dark: localStorage.getItem(\\\'dark\\\')===\\\'true\\\', mobileOpen: false }}" :class="dark ? \\\'dark\\\' : \\\'\\\'" class="scroll-smooth">\\n\'',
    '        f\'<head>\\n\'',
    '        f\'  <meta charset="UTF-8"/>\\n\'',
    '        f\'  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>\\n\'',
    '        f\'  <title>{name} &mdash; {page_title}</title>\\n\'',
    '        f\'  <script src="https://cdn.tailwindcss.com"></script>\\n\'',
    '        f\'  <script>\\n\'',
    '        f\'    tailwind.config = {{\\n\'',
    '        f\'      darkMode: \\\'class\\\',\\n\'',
    '        f\'      theme: {{ extend: {{ colors: {{ primary: {{ 50:\\\'#f5f3ff\\\', 500:\\\'{primary}\\\', 600:\\\'{dark}\\\' }}, secondary: {{ 500:\\\'{secondary}\\\' }} }}, fontFamily: {{ sans: [\\\'{font}\\\',\\\'system-ui\\\',\\\'sans-serif\\\'] }} }} }}\\n\'',
    '        f\'    }}\\n\'',
    '        f\'  </script>\\n\'',
    '        f\'  <link rel="preconnect" href="https://fonts.googleapis.com"/>\\n\'',
    '        f\'  <link href="https://fonts.googleapis.com/css2?family={font_url}:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>\\n\'',
    '        f\'  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>\\n\'',
    '        f\'  <link rel="stylesheet" href="style.css"/>\\n\'',
    '        f\'</head>\\n\'',
    '        f\'<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white font-sans antialiased">\\n\'',
    "    )",
    "",
    "",
    "def _sp2_nav(name: str) -> str:",
    '    """Generate the navbar for a Static Pro page."""',
    "    return (",
    '        f\'<nav id="navbar" class="sticky top-0 z-50 bg-white/95 dark:bg-gray-900/95 backdrop-blur border-b border-gray-200 dark:border-gray-800 transition-shadow">\\n\'',
    '        f\'  <div class="max-w-6xl mx-auto px-4 sm:px-6 flex items-center justify-between h-16">\\n\'',
    '        f\'    <a href="index.html" class="text-xl font-bold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">&#9889; {name}</a>\\n\'',
    '        \'    <ul class="hidden md:flex items-center gap-6 list-none">\\n\'',
    '        \'      <li><a href="index.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Home</a></li>\\n\'',
    '        \'      <li><a href="about.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">About</a></li>\\n\'',
    '        \'      <li><a href="services.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Services</a></li>\\n\'',
    '        \'      <li><a href="portfolio.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Portfolio</a></li>\\n\'',
    '        \'      <li><a href="blog.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Blog</a></li>\\n\'',
    '        \'      <li><a href="contact.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Contact</a></li>\\n\'',
    '        \'      <li><a href="pricing.html" data-nav class="text-sm font-medium bg-gradient-to-r from-primary-500 to-secondary-500 text-white px-4 py-1.5 rounded-full hover:opacity-90">Pricing</a></li>\\n\'',
    '        \'    </ul>\\n\'',
    '        \'    <div class="flex items-center gap-3">\\n\'',
    '        \'      <button @click="dark=!dark; localStorage.setItem(\\\'dark\\\', dark)" class="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" aria-label="Toggle dark mode">\\n\'',
    '        \'        <svg x-show="!dark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>\\n\'',
    '        \'        <svg x-show="dark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>\\n\'',
    '        \'      </button>\\n\'',
    '        \'      <button @click="mobileOpen=!mobileOpen" class="md:hidden p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" aria-label="Toggle menu">\\n\'',
    '        \'        <svg x-show="!mobileOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>\\n\'',
    '        \'        <svg x-show="mobileOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>\\n\'',
    '        \'      </button>\\n\'',
    '        \'    </div>\\n\'',
    '        \'  </div>\\n\'',
    '        \'  <div x-show="mobileOpen" x-cloak x-transition class="md:hidden border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-4 py-3 flex flex-col gap-3">\\n\'',
    '        \'    <a href="index.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Home</a>\\n\'',
    '        \'    <a href="about.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">About</a>\\n\'',
    '        \'    <a href="services.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Services</a>\\n\'',
    '        \'    <a href="portfolio.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Portfolio</a>\\n\'',
    '        \'    <a href="blog.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Blog</a>\\n\'',
    '        \'    <a href="contact.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Contact</a>\\n\'',
    '        \'    <a href="pricing.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-primary-500 font-semibold">Pricing</a>\\n\'',
    '        \'  </div>\\n\'',
    '        \'</nav>\\n\'',
    "    )",
    "",
    "",
    "def _sp2_footer(name: str) -> str:",
    '    """Generate the footer for a Static Pro page."""',
    "    email = name.lower().replace(' ', '') + '.io'",
    "    return (",
    '        f\'<footer class="bg-gray-900 dark:bg-gray-950 text-gray-400 pt-14 pb-6">\\n\'',
    '        f\'  <div class="max-w-6xl mx-auto px-4 sm:px-6">\\n\'',
    '        f\'    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-10">\\n\'',
    '        f\'      <div>\\n\'',
    '        f\'        <a href="index.html" class="text-xl font-bold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">&#9889; {name}</a>\\n\'',
    '        \'        <p class="mt-3 text-sm leading-relaxed">Building the future with cutting-edge technology. Trusted by teams worldwide.</p>\\n\'',
    '        \'        <div class="flex gap-3 mt-4">\\n\'',
    '        \'          <a href="#" class="w-8 h-8 rounded-lg bg-gray-800 hover:bg-primary-500 flex items-center justify-center transition-colors text-xs" aria-label="Twitter">&#120143;</a>\\n\'',
    '        \'          <a href="#" class="w-8 h-8 rounded-lg bg-gray-800 hover:bg-primary-500 flex items-center justify-center transition-colors text-xs" aria-label="LinkedIn">in</a>\\n\'',
    '        \'          <a href="#" class="w-8 h-8 rounded-lg bg-gray-800 hover:bg-primary-500 flex items-center justify-center transition-colors text-xs" aria-label="GitHub">GH</a>\\n\'',
    '        \'        </div>\\n\'',
    '        \'      </div>\\n\'',
    '        \'      <div><h4 class="text-white text-sm font-semibold mb-4">Pages</h4><ul class="space-y-2 text-sm">\\n\'',
    '        \'        <li><a href="index.html" class="hover:text-primary-500 transition-colors">Home</a></li>\\n\'',
    '        \'        <li><a href="about.html" class="hover:text-primary-500 transition-colors">About</a></li>\\n\'',
    '        \'        <li><a href="services.html" class="hover:text-primary-500 transition-colors">Services</a></li>\\n\'',
    '        \'        <li><a href="portfolio.html" class="hover:text-primary-500 transition-colors">Portfolio</a></li>\\n\'',
    '        \'        <li><a href="blog.html" class="hover:text-primary-500 transition-colors">Blog</a></li>\\n\'',
    '        \'      </ul></div>\\n\'',
    '        \'      <div><h4 class="text-white text-sm font-semibold mb-4">More</h4><ul class="space-y-2 text-sm">\\n\'',
    '        \'        <li><a href="pricing.html" class="hover:text-primary-500 transition-colors">Pricing</a></li>\\n\'',
    '        \'        <li><a href="team.html" class="hover:text-primary-500 transition-colors">Team</a></li>\\n\'',
    '        \'        <li><a href="faq.html" class="hover:text-primary-500 transition-colors">FAQ</a></li>\\n\'',
    '        \'        <li><a href="testimonials.html" class="hover:text-primary-500 transition-colors">Testimonials</a></li>\\n\'',
    '        \'        <li><a href="contact.html" class="hover:text-primary-500 transition-colors">Contact</a></li>\\n\'',
    '        \'      </ul></div>\\n\'',
    '        f\'      <div><h4 class="text-white text-sm font-semibold mb-4">Contact</h4><ul class="space-y-2 text-sm">\\n\'',
    '        f\'        <li>hello@{email}</li>\\n\'',
    '        \'        <li>+1 (555) 000-1234</li>\\n\'',
    '        \'        <li>123 Tech Ave, SF, CA</li>\\n\'',
    '        \'        <li>Mon-Fri 9am-6pm PST</li>\\n\'',
    '        \'      </ul></div>\\n\'',
    '        \'    </div>\\n\'',
    '        f\'    <div class="border-t border-gray-800 pt-6 flex flex-col sm:flex-row justify-between items-center gap-2 text-xs">\\n\'',
    '        f\'      <span>&copy; 2025 {name}. All rights reserved.</span>\\n\'',
    '        \'      <span>Made with &#10084;&#65039; for developers</span>\\n\'',
    '        \'    </div>\\n\'',
    '        \'  </div>\\n\'',
    '        \'</footer>\\n\'',
    '        \'<script src="script.js"></script>\\n\'',
    '        \'</body>\\n\'',
    '        \'</html>\\n\'',
    "    )",
    "",
    "",
    "def _sp2_page(name: str, primary: str, secondary: str, font: str, page_title: str, body: str) -> str:",
    '    """Assemble a complete Static Pro HTML page."""',
    "    return (",
    "        _sp2_head(name, primary, secondary, font, page_title)",
    "        + _sp2_nav(name)",
    "        + body",
    "        + _sp2_footer(name)",
    "    )",
    "",
    "",
    "def _gen_static(config: dict) -> dict:",
    '    """Generate a Static Pro 10-page website with Tailwind CSS + Alpine.js."""',
    "    name      = _c(config, 'site_name', 'My Website')",
    "    primary   = _c(config, 'primary_color', '#6c63ff')",
    "    secondary = _c(config, 'secondary_color', '#f50057')",
    "    font      = _c(config, 'font', 'Inter')",
    "",
    "    def pg(title, body_const):",
    "        return _sp2_page(name, primary, secondary, font, title, body_const)",
    "",
    "    css = _SP2_CSS.replace('PRIMARY_COLOR', primary).replace('SECONDARY_COLOR', secondary)",
    "",
    "    return {",
    "        'index.html':        pg('Home',         _SP2_INDEX_BODY),",
    "        'about.html':        pg('About',        _SP2_ABOUT_BODY),",
    "        'services.html':     pg('Services',     _SP2_SERVICES_BODY),",
    "        'portfolio.html':    pg('Portfolio',    _SP2_PORTFOLIO_BODY),",
    "        'blog.html':         pg('Blog',         _SP2_BLOG_BODY),",
    "        'contact.html':      pg('Contact',      _SP2_CONTACT_BODY),",
    "        'pricing.html':      pg('Pricing',      _SP2_PRICING_BODY),",
    "        'team.html':         pg('Team',         _SP2_TEAM_BODY),",
    "        'faq.html':          pg('FAQ',          _SP2_FAQ_BODY),",
    "        'testimonials.html': pg('Testimonials', _SP2_TESTIMONIALS_BODY),",
    "        'style.css':         css,",
    "        'script.js':         _SP2_JS,",
    "        'README.txt':        f'{name}\\nOpen index.html in your browser.\\nBuilt with Static Pro generator.\\n',",
    "    }",
    "",
]

override_text = "\n".join(override_lines)
pathlib.Path("website-generator/_gen_static_override.py").write_text(override_text, encoding="utf-8")
print(f"Override written: {len(override_text)} bytes, {override_text.count(chr(10))} lines")