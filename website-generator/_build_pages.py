"""Build all static-site HTML pages."""
import pathlib

BASE = pathlib.Path("static-site")


def w(name, content):
    (BASE / name).write_text(content, encoding="utf-8")
    print(f"wrote {name}")


# ── Shared snippets ────────────────────────────────────────────────────────────

HEAD_TMPL = """\
<!DOCTYPE html>
<html lang="en" x-data="{{ dark: localStorage.getItem('dark')==='true', mobileOpen: false }}" :class="dark ? 'dark' : ''" class="scroll-smooth">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>NovaTech &mdash; {page_title}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{ extend: {{ colors: {{ primary: {{ 50:'#f5f3ff', 500:'#6c63ff', 600:'#5a52d5' }}, secondary: {{ 500:'#f50057' }} }}, fontFamily: {{ sans: ['Inter','system-ui','sans-serif'] }} }} }}
    }}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
"""

NAVBAR = """\
<nav id="navbar" class="sticky top-0 z-50 bg-white/95 dark:bg-gray-900/95 backdrop-blur border-b border-gray-200 dark:border-gray-800 transition-shadow">
  <div class="max-w-6xl mx-auto px-4 sm:px-6 flex items-center justify-between h-16">
    <a href="index.html" class="text-xl font-bold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">&#9889; NovaTech</a>
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

FOOTER = """\
<footer class="bg-gray-900 dark:bg-gray-950 text-gray-400 pt-14 pb-6">
  <div class="max-w-6xl mx-auto px-4 sm:px-6">
    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-10">
      <div>
        <a href="index.html" class="text-xl font-bold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">&#9889; NovaTech</a>
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
          <li>hello@novatech.io</li>
          <li>+1 (555) 000-1234</li>
          <li>123 Tech Ave, SF, CA</li>
          <li>Mon-Fri 9am-6pm PST</li>
        </ul>
      </div>
    </div>
    <div class="border-t border-gray-800 pt-6 flex flex-col sm:flex-row justify-between items-center gap-2 text-xs">
      <span>&copy; 2025 NovaTech. All rights reserved.</span>
      <span>Made with &#10084;&#65039; for developers</span>
    </div>
  </div>
</footer>
<script src="script.js"></script>
</body>
</html>
"""


def page(title, body):
    return HEAD_TMPL.format(page_title=title) + NAVBAR + body + FOOTER


# ── services.html ──────────────────────────────────────────────────────────────

SERVICES_BODY = """\
<section class="py-20 px-4 sm:px-6 text-center bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-b border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto">
    <h1 class="text-4xl sm:text-5xl font-extrabold mb-4">Our <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Services</span></h1>
    <p class="text-gray-500 dark:text-gray-400 text-lg">End-to-end solutions for modern businesses — from infrastructure to AI.</p>
  </div>
</section>

<section class="py-20 px-4 sm:px-6">
  <div class="max-w-6xl mx-auto">
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-20">
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col gap-3">
        <div class="w-12 h-12 rounded-xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center text-2xl">&#9729;</div>
        <h3 class="font-semibold text-lg">Cloud Infrastructure</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Scalable, secure cloud infrastructure that grows with your business. Deploy anywhere in minutes.</p>
        <ul class="space-y-1 text-sm text-gray-500 dark:text-gray-400">
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Auto-scaling clusters</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> 99.99% uptime SLA</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Multi-region deployment</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Managed Kubernetes</li>
        </ul>
        <a href="contact.html" class="text-primary-500 text-sm font-semibold mt-auto">Learn more &#8594;</a>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col gap-3">
        <div class="w-12 h-12 rounded-xl bg-secondary-500/10 border border-secondary-500/20 flex items-center justify-center text-2xl">&#129302;</div>
        <h3 class="font-semibold text-lg">AI &amp; Machine Learning</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Integrate cutting-edge AI into your products with our managed ML platform and pre-built models.</p>
        <ul class="space-y-1 text-sm text-gray-500 dark:text-gray-400">
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Pre-trained model library</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Custom model training</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Real-time inference API</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> MLOps pipeline</li>
        </ul>
        <a href="contact.html" class="text-primary-500 text-sm font-semibold mt-auto">Learn more &#8594;</a>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col gap-3">
        <div class="w-12 h-12 rounded-xl bg-green-500/10 border border-green-500/20 flex items-center justify-center text-2xl">&#128274;</div>
        <h3 class="font-semibold text-lg">Security &amp; Compliance</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Enterprise-grade security with automated compliance monitoring for SOC 2, GDPR, and HIPAA.</p>
        <ul class="space-y-1 text-sm text-gray-500 dark:text-gray-400">
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Zero-trust architecture</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Automated threat detection</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> SOC 2 Type II certified</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Penetration testing</li>
        </ul>
        <a href="contact.html" class="text-primary-500 text-sm font-semibold mt-auto">Learn more &#8594;</a>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col gap-3">
        <div class="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-2xl">&#128202;</div>
        <h3 class="font-semibold text-lg">Analytics &amp; Monitoring</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Full-stack observability with real-time dashboards, alerting, and AI-powered anomaly detection.</p>
        <ul class="space-y-1 text-sm text-gray-500 dark:text-gray-400">
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Real-time dashboards</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Custom alerting rules</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Log aggregation</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Performance profiling</li>
        </ul>
        <a href="contact.html" class="text-primary-500 text-sm font-semibold mt-auto">Learn more &#8594;</a>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col gap-3">
        <div class="w-12 h-12 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center text-2xl">&#128279;</div>
        <h3 class="font-semibold text-lg">API &amp; Integrations</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Connect your stack with 200+ integrations and a powerful REST/GraphQL API platform.</p>
        <ul class="space-y-1 text-sm text-gray-500 dark:text-gray-400">
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> REST &amp; GraphQL APIs</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Webhook management</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> 200+ connectors</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> API gateway</li>
        </ul>
        <a href="contact.html" class="text-primary-500 text-sm font-semibold mt-auto">Learn more &#8594;</a>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col gap-3">
        <div class="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-2xl">&#128101;</div>
        <h3 class="font-semibold text-lg">Managed Support</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">24/7 expert support with dedicated account managers and guaranteed response times.</p>
        <ul class="space-y-1 text-sm text-gray-500 dark:text-gray-400">
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> 24/7 live chat &amp; phone</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Dedicated account manager</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> &lt;1hr response SLA</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Onboarding assistance</li>
        </ul>
        <a href="contact.html" class="text-primary-500 text-sm font-semibold mt-auto">Learn more &#8594;</a>
      </div>
    </div>

    <!-- Pricing tiers -->
    <div class="text-center mb-12 reveal">
      <h2 class="text-3xl font-bold mb-3">Simple <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Pricing</span></h2>
      <p class="text-gray-500 dark:text-gray-400">No hidden fees. Cancel anytime.</p>
    </div>
    <div class="grid sm:grid-cols-3 gap-6 mb-20">
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 flex flex-col gap-3">
        <div class="text-xs font-bold uppercase tracking-widest text-gray-500 dark:text-gray-400">Starter</div>
        <div class="text-4xl font-extrabold">$0<span class="text-base font-normal text-gray-500">/mo</span></div>
        <p class="text-sm text-gray-500 dark:text-gray-400">Perfect for side projects and early-stage startups.</p>
        <ul class="space-y-2 text-sm flex-1">
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> 3 projects</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> 10GB storage</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Community support</li>
          <li class="flex items-center gap-2 text-gray-400"><span>&#8212;</span> Custom domains</li>
          <li class="flex items-center gap-2 text-gray-400"><span>&#8212;</span> Analytics</li>
        </ul>
        <a href="contact.html" class="block text-center py-2.5 border border-gray-300 dark:border-gray-600 rounded-xl text-sm font-semibold hover:border-primary-500 hover:text-primary-500 transition-colors">Get Started Free</a>
      </div>
      <div class="reveal relative bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-2 border-primary-500 rounded-2xl p-6 flex flex-col gap-3">
        <div class="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white text-xs font-bold px-4 py-1 rounded-full">Most Popular</div>
        <div class="text-xs font-bold uppercase tracking-widest text-primary-500">Pro</div>
        <div class="text-4xl font-extrabold">$49<span class="text-base font-normal text-gray-500">/mo</span></div>
        <p class="text-sm text-gray-500 dark:text-gray-400">For growing teams that need more power and flexibility.</p>
        <ul class="space-y-2 text-sm flex-1">
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Unlimited projects</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> 100GB storage</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Priority support</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Custom domains</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Advanced analytics</li>
        </ul>
        <a href="contact.html" class="block text-center py-2.5 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl text-sm font-semibold hover:opacity-90 transition-opacity">Start Pro Trial</a>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 flex flex-col gap-3">
        <div class="text-xs font-bold uppercase tracking-widest text-gray-500 dark:text-gray-400">Enterprise</div>
        <div class="text-4xl font-extrabold">Custom</div>
        <p class="text-sm text-gray-500 dark:text-gray-400">Tailored solutions for large organizations with complex needs.</p>
        <ul class="space-y-2 text-sm flex-1">
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Everything in Pro</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Unlimited storage</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Dedicated support</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> SLA guarantee</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Custom contracts</li>
        </ul>
        <a href="contact.html" class="block text-center py-2.5 border border-gray-300 dark:border-gray-600 rounded-xl text-sm font-semibold hover:border-primary-500 hover:text-primary-500 transition-colors">Contact Sales</a>
      </div>
    </div>

    <!-- Process steps -->
    <div class="text-center mb-12 reveal">
      <h2 class="text-3xl font-bold mb-3">How It <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Works</span></h2>
    </div>
    <div class="grid sm:grid-cols-4 gap-6 text-center">
      <div class="reveal">
        <div class="text-4xl font-extrabold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent mb-2">01</div>
        <h3 class="font-semibold mb-1">Sign Up</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400">Create your account in under 60 seconds. No credit card required.</p>
      </div>
      <div class="reveal">
        <div class="text-4xl font-extrabold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent mb-2">02</div>
        <h3 class="font-semibold mb-1">Configure</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400">Set up your project with our guided wizard. Deploy in minutes.</p>
      </div>
      <div class="reveal">
        <div class="text-4xl font-extrabold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent mb-2">03</div>
        <h3 class="font-semibold mb-1">Integrate</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400">Connect your existing tools and workflows with one-click integrations.</p>
      </div>
      <div class="reveal">
        <div class="text-4xl font-extrabold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent mb-2">04</div>
        <h3 class="font-semibold mb-1">Scale</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400">Watch your product grow. We handle the infrastructure automatically.</p>
      </div>
    </div>
  </div>
</section>

<section class="py-20 px-4 sm:px-6 bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-t border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto text-center">
    <h2 class="text-3xl font-bold mb-4">Ready to <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Get Started?</span></h2>
    <p class="text-gray-500 dark:text-gray-400 mb-8">Join 10,000+ teams already building with NovaTech.</p>
    <div class="flex flex-wrap gap-4 justify-center">
      <a href="contact.html" class="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-full hover:opacity-90 transition-opacity shadow-lg">Start Free Trial</a>
      <a href="pricing.html" class="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold rounded-full hover:border-primary-500 hover:text-primary-500 transition-colors">View Pricing &#8594;</a>
    </div>
  </div>
</section>
"""


