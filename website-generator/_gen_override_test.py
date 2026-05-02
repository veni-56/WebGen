import pathlib

# Read the body files
WG = pathlib.Path("website-generator")

def _darken(hex_color):
    """Darken a hex color by ~15%."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    r = max(0, int(r * 0.85))
    g = max(0, int(g * 0.85))
    b = max(0, int(b * 0.85))
    return f"#{r:02x}{g:02x}{b:02x}"

def _sp2_head(name, primary, secondary, font):
    font_url = font.replace(" ", "+")
    return f"""<!DOCTYPE html>
<html lang="en" x-data="{{ dark: localStorage.getItem('dark')==='true', mobileOpen: false }}" :class="dark ? 'dark' : ''" class="scroll-smooth">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{name} &mdash; PAGE_TITLE</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{ extend: {{ colors: {{ primary: {{ 50:'#f5f3ff', 500:'{primary}', 600:'{_darken(primary)}' }}, secondary: {{ 500:'{secondary}' }} }}, fontFamily: {{ sans: ['{font}','system-ui','sans-serif'] }} }} }}
    }}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family={font_url}:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
  <link rel="stylesheet" href="style.css"/>
</head>
<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white font-sans antialiased">
"""

def _sp2_nav(name):
    return f"""<nav id="navbar" class="sticky top-0 z-50 bg-white/95 dark:bg-gray-900/95 backdrop-blur border-b border-gray-200 dark:border-gray-800 transition-shadow">
  <div class="max-w-6xl mx-auto px-4 sm:px-6 flex items-center justify-between h-16">
    <a href="index.html" class="text-xl font-bold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">&#9889; {name}</a>
    <ul class="hidden md:flex items-center gap-6 list-none">
      <li><a href="index.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Home</a></li>
      <li><a href="about.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">About</a></li>
      <li><a href="services.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Services</a></li>
      <li><a href="portfolio.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Portfolio</a></li>
      <li><a href="blog.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Blog</a></li>
      <li><a href="contact.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Contact</a></li>
      <li><a href="pricing.html" data-nav class="text-sm font-medium bg-gradient-to-r from-primary-500 to-secondary-500 text-white px-4 py-1.5 rounded-full hover:opacity-90">Pricing</a></li>
    </ul>
    <div class="flex items-center gap-3">
      <button @click="dark=!dark; localStorage.setItem('dark', dark)" class="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" aria-label="Toggle dark mode">
        <svg x-show="!dark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
        <svg x-show="dark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
      </button>
      <button @click="mobileOpen=!mobileOpen" class="md:hidden p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" aria-label="Toggle menu">
        <svg x-show="!mobileOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        <svg x-show="mobileOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
      </button>
    </div>
  </div>
  <div x-show="mobileOpen" x-cloak x-transition class="md:hidden border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-4 py-3 flex flex-col gap-3">
    <a href="index.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Home</a>
    <a href="about.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">About</a>
    <a href="services.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Services</a>
    <a href="portfolio.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Portfolio</a>
    <a href="blog.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Blog</a>
    <a href="contact.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Contact</a>
    <a href="pricing.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-primary-500 font-semibold">Pricing</a>
  </div>
</nav>
"""

def _sp2_footer(name):
    return f"""<footer class="bg-gray-900 dark:bg-gray-950 text-gray-400 pt-14 pb-6">
  <div class="max-w-6xl mx-auto px-4 sm:px-6">
    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-10">
      <div>
        <a href="index.html" class="text-xl font-bold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">&#9889; {name}</a>
        <p class="mt-3 text-sm leading-relaxed">Building the future with cutting-edge technology. Trusted by teams worldwide.</p>
        <div class="flex gap-3 mt-4">
          <a href="#" class="w-8 h-8 rounded-lg bg-gray-800 hover:bg-primary-500 flex items-center justify-center transition-colors text-xs" aria-label="Twitter">&#120143;</a>
          <a href="#" class="w-8 h-8 rounded-lg bg-gray-800 hover:bg-primary-500 flex items-center justify-center transition-colors text-xs" aria-label="LinkedIn">in</a>
          <a href="#" class="w-8 h-8 rounded-lg bg-gray-800 hover:bg-primary-500 flex items-center justify-center transition-colors text-xs" aria-label="GitHub">GH</a>
        </div>
      </div>
      <div>
        <h4 class="text-white text-sm font-semibold mb-4">Pages</h4>
        <ul class="space-y-2 text-sm">
          <li><a href="index.html" class="hover:text-primary-500 transition-colors">Home</a></li>
          <li><a href="about.html" class="hover:text-primary-500 transition-colors">About</a></li>
          <li><a href="services.html" class="hover:text-primary-500 transition-colors">Services</a></li>
          <li><a href="portfolio.html" class="hover:text-primary-500 transition-colors">Portfolio</a></li>
          <li><a href="blog.html" class="hover:text-primary-500 transition-colors">Blog</a></li>
        </ul>
      </div>
      <div>
        <h4 class="text-white text-sm font-semibold mb-4">More</h4>
        <ul class="space-y-2 text-sm">
          <li><a href="pricing.html" class="hover:text-primary-500 transition-colors">Pricing</a></li>
          <li><a href="team.html" class="hover:text-primary-500 transition-colors">Team</a></li>
          <li><a href="faq.html" class="hover:text-primary-500 transition-colors">FAQ</a></li>
          <li><a href="testimonials.html" class="hover:text-primary-500 transition-colors">Testimonials</a></li>
          <li><a href="contact.html" class="hover:text-primary-500 transition-colors">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4 class="text-white text-sm font-semibold mb-4">Contact</h4>
        <ul class="space-y-2 text-sm">
          <li>hello@{name.lower().replace(' ', '')}.io</li>
          <li>+1 (555) 000-1234</li>
          <li>123 Tech Ave, SF, CA</li>
          <li>Mon-Fri 9am-6pm PST</li>
        </ul>
      </div>
    </div>
    <div class="border-t border-gray-800 pt-6 flex flex-col sm:flex-row justify-between items-center gap-2 text-xs">
      <span>&copy; 2025 {name}. All rights reserved.</span>
      <span>Made with &#10084;&#65039; for developers</span>
    </div>
  </div>
</footer>
<script src="script.js"></script>
</body>
</html>
"""

print("override helpers ok")