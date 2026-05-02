

# ─────────────────────────────────────────────────────────────────────────────
# STATIC PRO GENERATOR — overrides _gen_static() with Tailwind + Alpine.js
# ─────────────────────────────────────────────────────────────────────────────

def _sp2_darken(hex_color: str) -> str:
    """Darken a hex color by ~15%."""
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f'#{max(0,int(r*.85)):02x}{max(0,int(g*.85)):02x}{max(0,int(b*.85)):02x}'

_SP2_INDEX_BODY = """<!-- ── Hero ────────────────────────────────────────────────────────────── -->
<section class="relative min-h-[calc(100vh-64px)] flex items-center overflow-hidden bg-gradient-to-br from-primary-500 via-purple-600 to-secondary-500">
  <div class="absolute inset-0 bg-black/30"></div>
  <div class="relative max-w-6xl mx-auto px-4 sm:px-6 py-20 grid md:grid-cols-2 gap-12 items-center w-full">
    <div>
      <div class="inline-block px-3 py-1 mb-5 text-xs font-semibold text-white/90 bg-white/10 border border-white/20 rounded-full">✨ Trusted by 10,000+ teams worldwide</div>
      <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white leading-tight mb-5">
        Build the Future<br><span class="text-yellow-300">Faster Than Ever</span>
      </h1>
      <p class="text-white/80 text-lg mb-8 max-w-md">NovaTech delivers cutting-edge software solutions that help businesses scale, innovate, and lead their industries.</p>
      <div class="flex flex-wrap gap-4">
        <a href="contact.html" class="px-6 py-3 bg-white text-primary-600 font-semibold rounded-full hover:bg-gray-100 transition-colors shadow-lg">Start Free Trial</a>
        <a href="about.html"   class="px-6 py-3 border border-white/40 text-white font-semibold rounded-full hover:bg-white/10 transition-colors">Learn More →</a>
      </div>
    </div>
    <!-- Code card visual -->
    <div class="hidden md:flex justify-center">
      <div class="relative bg-gray-900/90 border border-white/10 rounded-2xl p-6 w-full max-w-sm shadow-2xl">
        <div class="flex gap-1.5 mb-4">
          <span class="w-3 h-3 rounded-full bg-red-500"></span>
          <span class="w-3 h-3 rounded-full bg-yellow-400"></span>
          <span class="w-3 h-3 rounded-full bg-green-500"></span>
        </div>
        <pre class="font-mono text-sm leading-relaxed text-green-300"><code><span class="c-kw">const</span> <span class="c-fn">launch</span> = <span class="c-kw">async</span> () => {
  <span class="c-kw">const</span> product = <span class="c-kw">await</span>
    NovaTech.<span class="c-fn">build</span>({
      speed: <span class="c-str">"blazing"</span>,
      scale: <span class="c-num">Infinity</span>,
      quality: <span class="c-str">"premium"</span>
    });
  <span class="c-kw">return</span> product.<span class="c-fn">deploy</span>();
};</code></pre>
        <div class="absolute -top-4 right-4 bg-white/10 backdrop-blur border border-white/20 text-white text-xs font-semibold px-3 py-1.5 rounded-full float-anim">🚀 Deployed!</div>
        <div class="absolute -bottom-4 left-4 bg-white/10 backdrop-blur border border-white/20 text-white text-xs font-semibold px-3 py-1.5 rounded-full float-anim-delay">⚡ 99.9% Uptime</div>
      </div>
    </div>
  </div>
</section>

<!-- ── Stats bar ─────────────────────────────────────────────────────────── -->
<div class="stats-bar bg-gray-50 dark:bg-gray-800 border-y border-gray-200 dark:border-gray-700 py-10">
  <div class="max-w-6xl mx-auto px-4 sm:px-6 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
    <div class="reveal">
      <strong data-target="10000" data-suffix="+" class="block text-3xl font-extrabold text-primary-500">0</strong>
      <span class="text-sm text-gray-500 dark:text-gray-400">Happy Clients</span>
    </div>
    <div class="reveal">
      <strong data-target="500" data-suffix="+" class="block text-3xl font-extrabold text-primary-500">0</strong>
      <span class="text-sm text-gray-500 dark:text-gray-400">Projects Shipped</span>
    </div>
    <div class="reveal">
      <strong data-target="99" data-suffix=".9%" class="block text-3xl font-extrabold text-primary-500">0</strong>
      <span class="text-sm text-gray-500 dark:text-gray-400">Uptime SLA</span>
    </div>
    <div class="reveal">
      <strong data-target="24" data-suffix="/7" class="block text-3xl font-extrabold text-primary-500">0</strong>
      <span class="text-sm text-gray-500 dark:text-gray-400">Support</span>
    </div>
  </div>
</div>

<!-- ── Features ─────────────────────────────────────────────────────────── -->
<section class="py-20 px-4 sm:px-6">
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-14 reveal">
      <h2 class="text-3xl sm:text-4xl font-bold mb-3">Everything You Need to <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Scale</span></h2>
      <p class="text-gray-500 dark:text-gray-400 max-w-xl mx-auto">A complete platform built for modern teams who demand performance, reliability, and developer experience.</p>
    </div>
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="text-3xl mb-4">⚡</div>
        <h3 class="font-semibold text-lg mb-2">Lightning Performance</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Sub-100ms response times globally. Our edge network ensures your users always get the fastest experience possible.</p>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="text-3xl mb-4">🔒</div>
        <h3 class="font-semibold text-lg mb-2">Enterprise Security</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">SOC 2 Type II certified. End-to-end encryption, zero-trust architecture, and automated threat detection.</p>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="text-3xl mb-4">📈</div>
        <h3 class="font-semibold text-lg mb-2">Auto Scaling</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Handle traffic spikes effortlessly. Our infrastructure scales from 1 to 1 million users without configuration.</p>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="text-3xl mb-4">🤖</div>
        <h3 class="font-semibold text-lg mb-2">AI-Powered Insights</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Real-time analytics with AI recommendations. Understand your users and optimize performance automatically.</p>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="text-3xl mb-4">🔗</div>
        <h3 class="font-semibold text-lg mb-2">200+ Integrations</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Connect with Slack, GitHub, Stripe, and 200+ tools your team already uses. One-click setup.</p>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="text-3xl mb-4">🌍</div>
        <h3 class="font-semibold text-lg mb-2">Global CDN</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Deploy to 50+ edge locations worldwide. Your content is always close to your users, wherever they are.</p>
      </div>
    </div>
  </div>
</section>

<!-- ── Testimonials ──────────────────────────────────────────────────────── -->
<section class="py-20 px-4 sm:px-6 bg-gray-50 dark:bg-gray-800/50 border-y border-gray-200 dark:border-gray-700">
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-14 reveal">
      <h2 class="text-3xl sm:text-4xl font-bold mb-3">Loved by <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Thousands</span></h2>
      <p class="text-gray-500 dark:text-gray-400 max-w-xl mx-auto">Don't take our word for it — hear from the teams building with NovaTech every day.</p>
    </div>
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
        <div class="text-yellow-400 mb-3">★★★★★</div>
        <p class="text-gray-600 dark:text-gray-300 italic text-sm leading-relaxed mb-5">"NovaTech cut our deployment time by 80%. The auto-scaling alone saved us thousands in infrastructure costs."</p>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">SC</div>
          <div><strong class="block text-sm">Sarah Chen</strong><span class="text-xs text-gray-500 dark:text-gray-400">CTO, TechFlow Inc.</span></div>
        </div>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
        <div class="text-yellow-400 mb-3">★★★★★</div>
        <p class="text-gray-600 dark:text-gray-300 italic text-sm leading-relaxed mb-5">"The best developer experience I've had in 10 years. The documentation is excellent and support is incredibly fast."</p>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">MJ</div>
          <div><strong class="block text-sm">Marcus Johnson</strong><span class="text-xs text-gray-500 dark:text-gray-400">Lead Engineer, StartupX</span></div>
        </div>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
        <div class="text-yellow-400 mb-3">★★★★★</div>
        <p class="text-gray-600 dark:text-gray-300 italic text-sm leading-relaxed mb-5">"We migrated 50+ microservices to NovaTech in a weekend. Zero downtime, zero issues. Absolutely incredible."</p>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">AP</div>
          <div><strong class="block text-sm">Aisha Patel</strong><span class="text-xs text-gray-500 dark:text-gray-400">VP Engineering, ScaleUp</span></div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ── CTA ───────────────────────────────────────────────────────────────── -->
<section class="py-20 px-4 sm:px-6 bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-b border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto text-center">
    <h2 class="text-3xl sm:text-4xl font-bold mb-4">Ready to <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Get Started?</span></h2>
    <p class="text-gray-500 dark:text-gray-400 mb-8">Join 10,000+ teams already building with NovaTech. Free plan available — no credit card required.</p>
    <div class="flex flex-wrap gap-4 justify-center">
      <a href="contact.html" class="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-full hover:opacity-90 transition-opacity shadow-lg">Start Free Trial</a>
      <a href="about.html"   class="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold rounded-full hover:border-primary-500 hover:text-primary-500 transition-colors">Meet the Team →</a>
    </div>
  </div>
</section>

<!-- ── Footer ────────────────────────────────────────────────────────────── -->"""

_SP2_ABOUT_BODY = """<!-- ── Page Hero ─────────────────────────────────────────────────────────── -->
<section class="py-20 px-4 sm:px-6 text-center bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-b border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto">
    <h1 class="text-4xl sm:text-5xl font-extrabold mb-4">About <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">NovaTech</span></h1>
    <p class="text-gray-500 dark:text-gray-400 text-lg">We're a team of engineers, designers, and dreamers building the infrastructure that powers tomorrow's companies.</p>
  </div>
</section>

<!-- ── Story ─────────────────────────────────────────────────────────────── -->
<section class="py-20 px-4 sm:px-6">
  <div class="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
    <div class="reveal">
      <h2 class="text-3xl font-bold mb-4">Our <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Story</span></h2>
      <p class="text-gray-500 dark:text-gray-400 leading-relaxed mb-4">Founded in 2018, NovaTech started with a simple mission: make enterprise-grade infrastructure accessible to every developer. We were tired of watching great ideas fail because of technical complexity.</p>
      <p class="text-gray-500 dark:text-gray-400 leading-relaxed mb-4">Today, we power over 10,000 companies across 60 countries — from solo founders to Fortune 500 enterprises. Our platform handles billions of requests daily with 99.9% uptime.</p>
      <p class="text-gray-500 dark:text-gray-400 leading-relaxed">We believe the best technology is invisible. It just works, so you can focus on what matters: building products your users love.</p>
    </div>
    <div class="reveal grid grid-cols-2 gap-4">
      <div class="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center">
        <div class="text-3xl font-extrabold text-primary-500 mb-1">2018</div>
        <div class="text-sm text-gray-500 dark:text-gray-400">Founded</div>
      </div>
      <div class="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center">
        <div class="text-3xl font-extrabold text-primary-500 mb-1">10K+</div>
        <div class="text-sm text-gray-500 dark:text-gray-400">Customers</div>
      </div>
      <div class="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center">
        <div class="text-3xl font-extrabold text-primary-500 mb-1">60+</div>
        <div class="text-sm text-gray-500 dark:text-gray-400">Countries</div>
      </div>
      <div class="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center">
        <div class="text-3xl font-extrabold text-primary-500 mb-1">150+</div>
        <div class="text-sm text-gray-500 dark:text-gray-400">Team Members</div>
      </div>
    </div>
  </div>
</section>

<!-- ── Values ─────────────────────────────────────────────────────────────── -->
<section class="py-20 px-4 sm:px-6 bg-gray-50 dark:bg-gray-800/50 border-y border-gray-200 dark:border-gray-700">
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-14 reveal">
      <h2 class="text-3xl sm:text-4xl font-bold mb-3">Our <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Values</span></h2>
      <p class="text-gray-500 dark:text-gray-400 max-w-xl mx-auto">The principles that guide every decision we make.</p>
    </div>
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
        <h3 class="font-semibold mb-2 flex items-center gap-2">🚀 Move Fast</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">We ship quickly, iterate constantly, and never let perfect be the enemy of good.</p>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
        <h3 class="font-semibold mb-2 flex items-center gap-2">🔒 Trust First</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Security and reliability are non-negotiable. We earn trust through consistent action.</p>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
        <h3 class="font-semibold mb-2 flex items-center gap-2">🌍 Think Global</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">We build for developers everywhere, with infrastructure that spans the globe.</p>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
        <h3 class="font-semibold mb-2 flex items-center gap-2">🤝 Customer Obsessed</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Every feature, every fix, every decision starts with the customer's needs.</p>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
        <h3 class="font-semibold mb-2 flex items-center gap-2">💡 Stay Curious</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">We embrace new ideas, challenge assumptions, and never stop learning.</p>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
        <h3 class="font-semibold mb-2 flex items-center gap-2">♻️ Sustainable</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">We're committed to carbon-neutral infrastructure and responsible growth.</p>
      </div>
    </div>
  </div>
</section>

<!-- ── Team Preview ───────────────────────────────────────────────────────── -->
<section class="py-20 px-4 sm:px-6">
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-14 reveal">
      <h2 class="text-3xl sm:text-4xl font-bold mb-3">Meet the <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Leadership</span></h2>
      <p class="text-gray-500 dark:text-gray-400 max-w-xl mx-auto">The people driving NovaTech's mission forward.</p>
    </div>
    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="w-16 h-16 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xl font-bold mx-auto mb-4">AK</div>
        <h3 class="font-semibold">Alex Kim</h3>
        <span class="text-xs text-primary-500 font-semibold">CEO & Co-Founder</span>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="w-16 h-16 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xl font-bold mx-auto mb-4">SR</div>
        <h3 class="font-semibold">Sofia Reyes</h3>
        <span class="text-xs text-primary-500 font-semibold">CTO & Co-Founder</span>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="w-16 h-16 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xl font-bold mx-auto mb-4">JL</div>
        <h3 class="font-semibold">James Liu</h3>
        <span class="text-xs text-primary-500 font-semibold">VP Engineering</span>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="w-16 h-16 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xl font-bold mx-auto mb-4">MP</div>
        <h3 class="font-semibold">Maya Patel</h3>
        <span class="text-xs text-primary-500 font-semibold">Head of Design</span>
      </div>
    </div>
    <div class="text-center mt-8">
      <a href="team.html" class="inline-block px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold rounded-full hover:border-primary-500 hover:text-primary-500 transition-colors">View Full Team →</a>
    </div>
  </div>
</section>

<!-- ── CTA ───────────────────────────────────────────────────────────────── -->
<section class="py-20 px-4 sm:px-6 bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-t border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto text-center">
    <h2 class="text-3xl sm:text-4xl font-bold mb-4">Join Our <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Journey</span></h2>
    <p class="text-gray-500 dark:text-gray-400 mb-8">We're always looking for talented people who share our passion for building great software.</p>
    <div class="flex flex-wrap gap-4 justify-center">
      <a href="contact.html" class="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-full hover:opacity-90 transition-opacity shadow-lg">Get in Touch</a>
      <a href="services.html" class="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold rounded-full hover:border-primary-500 hover:text-primary-500 transition-colors">Our Services →</a>
    </div>
  </div>
</section>

<!-- ── Footer ────────────────────────────────────────────────────────────── -->"""

_SP2_SERVICES_BODY = """﻿<section class="py-20 px-4 sm:px-6 text-center bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-b border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto">
    <h1 class="text-4xl sm:text-5xl font-extrabold mb-4">Our <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Services</span></h1>
    <p class="text-gray-500 dark:text-gray-400 text-lg">End-to-end solutions for modern businesses.</p>
  </div>
</section>
<section class="py-20 px-4 sm:px-6">
  <div class="max-w-6xl mx-auto">
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-20">
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col gap-3">
        <div class="w-12 h-12 rounded-xl bg-primary-500/10 flex items-center justify-center text-2xl">&#9729;</div>
        <h3 class="font-semibold text-lg">Cloud Infrastructure</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Scalable, secure cloud infrastructure that grows with your business.</p>
        <ul class="space-y-1 text-sm text-gray-500 dark:text-gray-400">
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Auto-scaling clusters</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> 99.99% uptime SLA</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Multi-region deployment</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Managed Kubernetes</li>
        </ul>
        <a href="contact.html" class="text-primary-500 text-sm font-semibold mt-auto">Learn more &#8594;</a>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col gap-3">
        <div class="w-12 h-12 rounded-xl bg-secondary-500/10 flex items-center justify-center text-2xl">&#129302;</div>
        <h3 class="font-semibold text-lg">AI &amp; Machine Learning</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Integrate cutting-edge AI into your products with our managed ML platform.</p>
        <ul class="space-y-1 text-sm text-gray-500 dark:text-gray-400">
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Pre-trained model library</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Custom model training</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Real-time inference API</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> MLOps pipeline</li>
        </ul>
        <a href="contact.html" class="text-primary-500 text-sm font-semibold mt-auto">Learn more &#8594;</a>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col gap-3">
        <div class="w-12 h-12 rounded-xl bg-green-500/10 flex items-center justify-center text-2xl">&#128274;</div>
        <h3 class="font-semibold text-lg">Security &amp; Compliance</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Enterprise-grade security with automated compliance monitoring.</p>
        <ul class="space-y-1 text-sm text-gray-500 dark:text-gray-400">
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Zero-trust architecture</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Automated threat detection</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> SOC 2 Type II certified</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Penetration testing</li>
        </ul>
        <a href="contact.html" class="text-primary-500 text-sm font-semibold mt-auto">Learn more &#8594;</a>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col gap-3">
        <div class="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center text-2xl">&#128202;</div>
        <h3 class="font-semibold text-lg">Analytics &amp; Monitoring</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Full-stack observability with real-time dashboards and AI-powered anomaly detection.</p>
        <ul class="space-y-1 text-sm text-gray-500 dark:text-gray-400">
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Real-time dashboards</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Custom alerting rules</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Log aggregation</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Performance profiling</li>
        </ul>
        <a href="contact.html" class="text-primary-500 text-sm font-semibold mt-auto">Learn more &#8594;</a>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col gap-3">
        <div class="w-12 h-12 rounded-xl bg-orange-500/10 flex items-center justify-center text-2xl">&#128279;</div>
        <h3 class="font-semibold text-lg">API &amp; Integrations</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Connect your stack with 200+ integrations and a powerful API platform.</p>
        <ul class="space-y-1 text-sm text-gray-500 dark:text-gray-400">
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> REST &amp; GraphQL APIs</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> Webhook management</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> 200+ connectors</li>
          <li class="flex items-center gap-2"><span class="text-primary-500 font-bold">&#10003;</span> API gateway</li>
        </ul>
        <a href="contact.html" class="text-primary-500 text-sm font-semibold mt-auto">Learn more &#8594;</a>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col gap-3">
        <div class="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center text-2xl">&#128101;</div>
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
    <div class="text-center mb-12 reveal">
      <h2 class="text-3xl font-bold mb-3">Simple <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Pricing</span></h2>
      <p class="text-gray-500 dark:text-gray-400">No hidden fees. Cancel anytime.</p>
    </div>
    <div class="grid sm:grid-cols-3 gap-6 mb-20">
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 flex flex-col gap-3">
        <div class="text-xs font-bold uppercase tracking-widest text-gray-500">Starter</div>
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
        <p class="text-sm text-gray-500 dark:text-gray-400">For growing teams that need more power.</p>
        <ul class="space-y-2 text-sm flex-1">
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Unlimited projects</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> 100GB storage</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Priority support</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Custom domains</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Advanced analytics</li>
        </ul>
        <a href="contact.html" class="block text-center py-2.5 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl text-sm font-semibold hover:opacity-90">Start Pro Trial</a>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 flex flex-col gap-3">
        <div class="text-xs font-bold uppercase tracking-widest text-gray-500">Enterprise</div>
        <div class="text-4xl font-extrabold">Custom</div>
        <p class="text-sm text-gray-500 dark:text-gray-400">Tailored solutions for large organizations.</p>
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
    <div class="text-center mb-12 reveal">
      <h2 class="text-3xl font-bold mb-3">How It <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Works</span></h2>
    </div>
    <div class="grid sm:grid-cols-4 gap-6 text-center mb-20">
      <div class="reveal"><div class="text-4xl font-extrabold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent mb-2">01</div><h3 class="font-semibold mb-1">Sign Up</h3><p class="text-sm text-gray-500 dark:text-gray-400">Create your account in 60 seconds. No credit card required.</p></div>
      <div class="reveal"><div class="text-4xl font-extrabold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent mb-2">02</div><h3 class="font-semibold mb-1">Configure</h3><p class="text-sm text-gray-500 dark:text-gray-400">Set up your project with our guided wizard.</p></div>
      <div class="reveal"><div class="text-4xl font-extrabold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent mb-2">03</div><h3 class="font-semibold mb-1">Integrate</h3><p class="text-sm text-gray-500 dark:text-gray-400">Connect your existing tools with one-click integrations.</p></div>
      <div class="reveal"><div class="text-4xl font-extrabold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent mb-2">04</div><h3 class="font-semibold mb-1">Scale</h3><p class="text-sm text-gray-500 dark:text-gray-400">Watch your product grow. We handle the infrastructure.</p></div>
    </div>
  </div>
</section>
<section class="py-20 px-4 sm:px-6 bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-t border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto text-center">
    <h2 class="text-3xl font-bold mb-4">Ready to <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Get Started?</span></h2>
    <p class="text-gray-500 dark:text-gray-400 mb-8">Join 10,000+ teams already building with NovaTech.</p>
    <div class="flex flex-wrap gap-4 justify-center">
      <a href="contact.html" class="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-full hover:opacity-90 shadow-lg">Start Free Trial</a>
      <a href="pricing.html" class="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold rounded-full hover:border-primary-500 hover:text-primary-500 transition-colors">View Pricing &#8594;</a>
    </div>
  </div>
</section>"""

_SP2_PORTFOLIO_BODY = """﻿<section class="py-20 px-4 sm:px-6 text-center bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-b border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto">
    <h1 class="text-4xl sm:text-5xl font-extrabold mb-4">Our <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Portfolio</span></h1>
    <p class="text-gray-500 dark:text-gray-400 text-lg">A selection of projects we are proud to have built.</p>
  </div>
</section>
<section class="py-20 px-4 sm:px-6">
  <div class="max-w-6xl mx-auto">
    <div class="flex flex-wrap gap-3 justify-center mb-10">
      <button data-filter="all" class="filter-btn px-4 py-1.5 rounded-full text-sm font-medium border bg-primary-500 text-white border-primary-500 transition-all">All</button>
      <button data-filter="web" class="filter-btn px-4 py-1.5 rounded-full text-sm font-medium border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:border-primary-500 hover:text-primary-500 transition-all">Web</button>
      <button data-filter="mobile" class="filter-btn px-4 py-1.5 rounded-full text-sm font-medium border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:border-primary-500 hover:text-primary-500 transition-all">Mobile</button>
      <button data-filter="branding" class="filter-btn px-4 py-1.5 rounded-full text-sm font-medium border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:border-primary-500 hover:text-primary-500 transition-all">Branding</button>
    </div>
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div class="portfolio-item reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl overflow-hidden hover:border-primary-500 hover:-translate-y-1 transition-all" data-category="web">
        <div class="relative h-48 overflow-hidden group">
          <img src="https://picsum.photos/seed/p1/600/400" alt="CloudDash" class="w-full h-full object-cover"/>
          <div class="absolute inset-0 bg-primary-500/80 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <span class="text-white text-sm font-semibold border border-white/40 px-3 py-1 rounded-full">View Project</span>
          </div>
        </div>
        <div class="p-5">
          <h3 class="font-semibold mb-1">CloudDash</h3>
          <p class="text-xs text-primary-500 font-semibold mb-2">Web Application</p>
          <div class="flex flex-wrap gap-1.5">
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">React</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">Node.js</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">AWS</span>
          </div>
        </div>
      </div>
      <div class="portfolio-item reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl overflow-hidden hover:border-primary-500 hover:-translate-y-1 transition-all" data-category="mobile">
        <div class="relative h-48 overflow-hidden group">
          <img src="https://picsum.photos/seed/p2/600/400" alt="PayFlow" class="w-full h-full object-cover"/>
          <div class="absolute inset-0 bg-primary-500/80 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <span class="text-white text-sm font-semibold border border-white/40 px-3 py-1 rounded-full">View Project</span>
          </div>
        </div>
        <div class="p-5">
          <h3 class="font-semibold mb-1">PayFlow</h3>
          <p class="text-xs text-primary-500 font-semibold mb-2">Mobile App</p>
          <div class="flex flex-wrap gap-1.5">
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">React Native</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">Stripe</span>
          </div>
        </div>
      </div>
      <div class="portfolio-item reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl overflow-hidden hover:border-primary-500 hover:-translate-y-1 transition-all" data-category="branding">
        <div class="relative h-48 overflow-hidden group">
          <img src="https://picsum.photos/seed/p3/600/400" alt="NexaBrand" class="w-full h-full object-cover"/>
          <div class="absolute inset-0 bg-primary-500/80 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <span class="text-white text-sm font-semibold border border-white/40 px-3 py-1 rounded-full">View Project</span>
          </div>
        </div>
        <div class="p-5">
          <h3 class="font-semibold mb-1">NexaBrand</h3>
          <p class="text-xs text-primary-500 font-semibold mb-2">Brand Identity</p>
          <div class="flex flex-wrap gap-1.5">
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">Figma</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">Illustrator</span>
          </div>
        </div>
      </div>
      <div class="portfolio-item reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl overflow-hidden hover:border-primary-500 hover:-translate-y-1 transition-all" data-category="web">
        <div class="relative h-48 overflow-hidden group">
          <img src="https://picsum.photos/seed/p4/600/400" alt="DataPulse" class="w-full h-full object-cover"/>
          <div class="absolute inset-0 bg-primary-500/80 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <span class="text-white text-sm font-semibold border border-white/40 px-3 py-1 rounded-full">View Project</span>
          </div>
        </div>
        <div class="p-5">
          <h3 class="font-semibold mb-1">DataPulse</h3>
          <p class="text-xs text-primary-500 font-semibold mb-2">Web Application</p>
          <div class="flex flex-wrap gap-1.5">
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">Vue.js</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">Python</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">PostgreSQL</span>
          </div>
        </div>
      </div>
      <div class="portfolio-item reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl overflow-hidden hover:border-primary-500 hover:-translate-y-1 transition-all" data-category="mobile">
        <div class="relative h-48 overflow-hidden group">
          <img src="https://picsum.photos/seed/p5/600/400" alt="FitTrack" class="w-full h-full object-cover"/>
          <div class="absolute inset-0 bg-primary-500/80 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <span class="text-white text-sm font-semibold border border-white/40 px-3 py-1 rounded-full">View Project</span>
          </div>
        </div>
        <div class="p-5">
          <h3 class="font-semibold mb-1">FitTrack</h3>
          <p class="text-xs text-primary-500 font-semibold mb-2">Mobile App</p>
          <div class="flex flex-wrap gap-1.5">
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">Flutter</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">Firebase</span>
          </div>
        </div>
      </div>
      <div class="portfolio-item reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl overflow-hidden hover:border-primary-500 hover:-translate-y-1 transition-all" data-category="branding">
        <div class="relative h-48 overflow-hidden group">
          <img src="https://picsum.photos/seed/p6/600/400" alt="GreenLeaf" class="w-full h-full object-cover"/>
          <div class="absolute inset-0 bg-primary-500/80 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <span class="text-white text-sm font-semibold border border-white/40 px-3 py-1 rounded-full">View Project</span>
          </div>
        </div>
        <div class="p-5">
          <h3 class="font-semibold mb-1">GreenLeaf</h3>
          <p class="text-xs text-primary-500 font-semibold mb-2">Brand Identity</p>
          <div class="flex flex-wrap gap-1.5">
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">Branding</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">Motion</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>"""

_SP2_BLOG_BODY = """﻿<section class="py-20 px-4 sm:px-6 text-center bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-b border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto">
    <h1 class="text-4xl sm:text-5xl font-extrabold mb-4">Our <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Blog</span></h1>
    <p class="text-gray-500 dark:text-gray-400 text-lg">Insights, tutorials, and updates from the NovaTech team.</p>
  </div>
</section>
<section class="py-20 px-4 sm:px-6">
  <div class="max-w-6xl mx-auto grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
    <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl overflow-hidden hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col">
      <img src="https://picsum.photos/seed/b1/600/300" alt="Blog post" class="w-full h-48 object-cover"/>
      <div class="p-5 flex flex-col flex-1">
        <span class="inline-block px-2.5 py-0.5 mb-3 text-xs font-bold uppercase tracking-wide bg-primary-500/10 text-primary-500 border border-primary-500/20 rounded-full">Infrastructure</span>
        <h3 class="font-semibold text-lg mb-2 leading-snug">The Future of Cloud Infrastructure in 2025</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed flex-1">Exploring the trends that will shape cloud computing over the next decade and how to prepare your stack.</p>
        <div class="flex items-center gap-3 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          <div class="w-7 h-7 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">AK</div>
          <span class="text-xs text-gray-500 dark:text-gray-400">Alex Kim &bull; Jan 15, 2025</span>
          <a href="#" class="ml-auto text-primary-500 text-xs font-semibold hover:underline">Read more &#8594;</a>
        </div>
      </div>
    </div>
    <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl overflow-hidden hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col">
      <img src="https://picsum.photos/seed/b2/600/300" alt="Blog post" class="w-full h-48 object-cover"/>
      <div class="p-5 flex flex-col flex-1">
        <span class="inline-block px-2.5 py-0.5 mb-3 text-xs font-bold uppercase tracking-wide bg-primary-500/10 text-primary-500 border border-primary-500/20 rounded-full">Security</span>
        <h3 class="font-semibold text-lg mb-2 leading-snug">Zero-Trust Architecture: A Practical Guide</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed flex-1">How to implement zero-trust security in your organization without disrupting existing workflows.</p>
        <div class="flex items-center gap-3 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          <div class="w-7 h-7 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">SR</div>
          <span class="text-xs text-gray-500 dark:text-gray-400">Sofia Reyes &bull; Jan 10, 2025</span>
          <a href="#" class="ml-auto text-primary-500 text-xs font-semibold hover:underline">Read more &#8594;</a>
        </div>
      </div>
    </div>
    <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl overflow-hidden hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col">
      <img src="https://picsum.photos/seed/b3/600/300" alt="Blog post" class="w-full h-48 object-cover"/>
      <div class="p-5 flex flex-col flex-1">
        <span class="inline-block px-2.5 py-0.5 mb-3 text-xs font-bold uppercase tracking-wide bg-primary-500/10 text-primary-500 border border-primary-500/20 rounded-full">AI</span>
        <h3 class="font-semibold text-lg mb-2 leading-snug">Building Scalable ML Pipelines with NovaTech</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed flex-1">A step-by-step walkthrough of building production-ready machine learning pipelines at scale.</p>
        <div class="flex items-center gap-3 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          <div class="w-7 h-7 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">JL</div>
          <span class="text-xs text-gray-500 dark:text-gray-400">James Liu &bull; Jan 5, 2025</span>
          <a href="#" class="ml-auto text-primary-500 text-xs font-semibold hover:underline">Read more &#8594;</a>
        </div>
      </div>
    </div>
    <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl overflow-hidden hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col">
      <img src="https://picsum.photos/seed/b4/600/300" alt="Blog post" class="w-full h-48 object-cover"/>
      <div class="p-5 flex flex-col flex-1">
        <span class="inline-block px-2.5 py-0.5 mb-3 text-xs font-bold uppercase tracking-wide bg-primary-500/10 text-primary-500 border border-primary-500/20 rounded-full">DevOps</span>
        <h3 class="font-semibold text-lg mb-2 leading-snug">Kubernetes Best Practices for Production</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed flex-1">Lessons learned from running Kubernetes in production across hundreds of enterprise deployments.</p>
        <div class="flex items-center gap-3 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          <div class="w-7 h-7 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">MP</div>
          <span class="text-xs text-gray-500 dark:text-gray-400">Maya Patel &bull; Dec 28, 2024</span>
          <a href="#" class="ml-auto text-primary-500 text-xs font-semibold hover:underline">Read more &#8594;</a>
        </div>
      </div>
    </div>
    <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl overflow-hidden hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col">
      <img src="https://picsum.photos/seed/b5/600/300" alt="Blog post" class="w-full h-48 object-cover"/>
      <div class="p-5 flex flex-col flex-1">
        <span class="inline-block px-2.5 py-0.5 mb-3 text-xs font-bold uppercase tracking-wide bg-primary-500/10 text-primary-500 border border-primary-500/20 rounded-full">Performance</span>
        <h3 class="font-semibold text-lg mb-2 leading-snug">Achieving Sub-100ms API Response Times</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed flex-1">Techniques and architecture patterns for building blazing-fast APIs that delight your users.</p>
        <div class="flex items-center gap-3 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          <div class="w-7 h-7 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">AK</div>
          <span class="text-xs text-gray-500 dark:text-gray-400">Alex Kim &bull; Dec 20, 2024</span>
          <a href="#" class="ml-auto text-primary-500 text-xs font-semibold hover:underline">Read more &#8594;</a>
        </div>
      </div>
    </div>
    <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl overflow-hidden hover:border-primary-500 hover:-translate-y-1 transition-all flex flex-col">
      <img src="https://picsum.photos/seed/b6/600/300" alt="Blog post" class="w-full h-48 object-cover"/>
      <div class="p-5 flex flex-col flex-1">
        <span class="inline-block px-2.5 py-0.5 mb-3 text-xs font-bold uppercase tracking-wide bg-primary-500/10 text-primary-500 border border-primary-500/20 rounded-full">Product</span>
        <h3 class="font-semibold text-lg mb-2 leading-snug">NovaTech 2025 Roadmap: What's Coming</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed flex-1">A sneak peek at the features and improvements we are shipping in 2025 based on your feedback.</p>
        <div class="flex items-center gap-3 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          <div class="w-7 h-7 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">SR</div>
          <span class="text-xs text-gray-500 dark:text-gray-400">Sofia Reyes &bull; Dec 15, 2024</span>
          <a href="#" class="ml-auto text-primary-500 text-xs font-semibold hover:underline">Read more &#8594;</a>
        </div>
      </div>
    </div>
  </div>
</section>"""

_SP2_CONTACT_BODY = """﻿<section class="py-20 px-4 sm:px-6 text-center bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-b border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto">
    <h1 class="text-4xl sm:text-5xl font-extrabold mb-4">Get in <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Touch</span></h1>
    <p class="text-gray-500 dark:text-gray-400 text-lg">We would love to hear from you. Send us a message and we will respond within 24 hours.</p>
  </div>
</section>
<section class="py-20 px-4 sm:px-6">
  <div class="max-w-6xl mx-auto grid md:grid-cols-2 gap-12">
    <div>
      <h2 class="text-2xl font-bold mb-4">Contact Information</h2>
      <p class="text-gray-500 dark:text-gray-400 mb-8 leading-relaxed">Have a question or want to work together? Fill out the form or reach us directly through any of the channels below.</p>
      <div class="space-y-4">
        <div class="flex items-center gap-4 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4">
          <div class="text-2xl flex-shrink-0">&#128231;</div>
          <div><strong class="block text-sm">Email</strong><span class="text-sm text-gray-500 dark:text-gray-400">hello@novatech.io</span></div>
        </div>
        <div class="flex items-center gap-4 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4">
          <div class="text-2xl flex-shrink-0">&#128222;</div>
          <div><strong class="block text-sm">Phone</strong><span class="text-sm text-gray-500 dark:text-gray-400">+1 (555) 000-1234</span></div>
        </div>
        <div class="flex items-center gap-4 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4">
          <div class="text-2xl flex-shrink-0">&#128205;</div>
          <div><strong class="block text-sm">Address</strong><span class="text-sm text-gray-500 dark:text-gray-400">123 Tech Ave, San Francisco, CA 94105</span></div>
        </div>
        <div class="flex items-center gap-4 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4">
          <div class="text-2xl flex-shrink-0">&#128336;</div>
          <div><strong class="block text-sm">Hours</strong><span class="text-sm text-gray-500 dark:text-gray-400">Mon-Fri 9am-6pm PST</span></div>
        </div>
      </div>
      <div class="mt-10" x-data="{ open: null }">
        <h3 class="font-semibold text-lg mb-4">Quick FAQ</h3>
        <div class="space-y-3">
          <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===0 ? 'border-primary-500' : ''">
            <button @click="open = open===0 ? null : 0" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">
              How quickly do you respond?
              <span class="text-primary-500 text-lg" x-text="open===0 ? '&#8722;' : '&#43;'">+</span>
            </button>
            <div x-show="open===0" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">We respond to all inquiries within 24 hours on business days. For urgent matters, call us directly.</div>
          </div>
          <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===1 ? 'border-primary-500' : ''">
            <button @click="open = open===1 ? null : 1" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">
              Do you offer free consultations?
              <span class="text-primary-500 text-lg" x-text="open===1 ? '&#8722;' : '&#43;'">+</span>
            </button>
            <div x-show="open===1" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">Yes! We offer a free 30-minute consultation to understand your needs and see if we are a good fit.</div>
          </div>
          <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===2 ? 'border-primary-500' : ''">
            <button @click="open = open===2 ? null : 2" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">
              What is your typical project timeline?
              <span class="text-primary-500 text-lg" x-text="open===2 ? '&#8722;' : '&#43;'">+</span>
            </button>
            <div x-show="open===2" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">Most projects take 4-12 weeks depending on scope. We will give you a detailed timeline during the consultation.</div>
          </div>
          <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===3 ? 'border-primary-500' : ''">
            <button @click="open = open===3 ? null : 3" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">
              Do you work with international clients?
              <span class="text-primary-500 text-lg" x-text="open===3 ? '&#8722;' : '&#43;'">+</span>
            </button>
            <div x-show="open===3" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">Absolutely! We work with clients in 60+ countries. Our team is distributed globally to support all time zones.</div>
          </div>
        </div>
      </div>
    </div>
    <div x-data="{ submitted: false }">
      <div x-show="!submitted" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-8">
        <h2 class="text-xl font-bold mb-6">Send a Message</h2>
        <form @submit.prevent="submitted=true; showToast('Message sent! We\\'ll get back to you soon. &#10003;')">
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">First Name</label>
              <input type="text" required placeholder="Alex" class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:border-primary-500 transition-colors"/>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">Last Name</label>
              <input type="text" required placeholder="Kim" class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:border-primary-500 transition-colors"/>
            </div>
          </div>
          <div class="mb-4">
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">Email</label>
            <input type="email" required placeholder="alex@company.com" class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:border-primary-500 transition-colors"/>
          </div>
          <div class="mb-4">
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">Company</label>
            <input type="text" placeholder="Acme Corp" class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:border-primary-500 transition-colors"/>
          </div>
          <div class="mb-4">
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">Subject</label>
            <select class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:border-primary-500 transition-colors">
              <option>General Inquiry</option>
              <option>Sales</option>
              <option>Technical Support</option>
              <option>Partnership</option>
              <option>Other</option>
            </select>
          </div>
          <div class="mb-6">
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">Message</label>
            <textarea required rows="4" placeholder="Tell us about your project..." class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:border-primary-500 transition-colors resize-none"></textarea>
          </div>
          <button type="submit" class="w-full py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-xl hover:opacity-90 transition-opacity">Send Message</button>
        </form>
      </div>
      <div x-show="submitted" x-cloak class="bg-white dark:bg-gray-800 border border-green-500 rounded-2xl p-8 text-center">
        <div class="text-5xl mb-4">&#10003;</div>
        <h3 class="text-xl font-bold text-green-600 dark:text-green-400 mb-2">Message Sent!</h3>
        <p class="text-gray-500 dark:text-gray-400">Thank you for reaching out. We will get back to you within 24 hours.</p>
        <button @click="submitted=false" class="mt-6 px-6 py-2.5 border border-gray-300 dark:border-gray-600 rounded-xl text-sm font-semibold hover:border-primary-500 hover:text-primary-500 transition-colors">Send Another</button>
      </div>
    </div>
  </div>
</section>"""

_SP2_PRICING_BODY = """﻿<section class="py-20 px-4 sm:px-6 text-center bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-b border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto">
    <h1 class="text-4xl sm:text-5xl font-extrabold mb-4">Simple, Transparent <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Pricing</span></h1>
    <p class="text-gray-500 dark:text-gray-400 text-lg">No hidden fees. No surprises. Cancel anytime.</p>
  </div>
</section>
<section class="py-20 px-4 sm:px-6" x-data="{ yearly: false }">
  <div class="max-w-6xl mx-auto">
    <div class="flex items-center justify-center gap-4 mb-12">
      <span class="text-sm font-medium" :class="!yearly ? 'text-primary-500' : 'text-gray-500 dark:text-gray-400'">Monthly</span>
      <button @click="yearly=!yearly" class="relative w-12 h-6 rounded-full transition-colors" :class="yearly ? 'bg-primary-500' : 'bg-gray-300 dark:bg-gray-600'">
        <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform" :class="yearly ? 'translate-x-6' : 'translate-x-0'"></span>
      </button>
      <span class="text-sm font-medium" :class="yearly ? 'text-primary-500' : 'text-gray-500 dark:text-gray-400'">Yearly <span class="text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-1.5 py-0.5 rounded-full font-semibold">Save 20%</span></span>
    </div>
    <div class="grid sm:grid-cols-3 gap-6 mb-20">
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 flex flex-col gap-3">
        <div class="text-xs font-bold uppercase tracking-widest text-gray-500">Starter</div>
        <div class="text-4xl font-extrabold">
          <span x-text="yearly ? '$0' : '$0'">$0</span><span class="text-base font-normal text-gray-500">/mo</span>
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400">Perfect for side projects and early-stage startups.</p>
        <ul class="space-y-2 text-sm flex-1">
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> 3 projects</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> 10GB storage</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Community support</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Basic analytics</li>
          <li class="flex items-center gap-2 text-gray-400"><span>&#8212;</span> Custom domains</li>
          <li class="flex items-center gap-2 text-gray-400"><span>&#8212;</span> Priority support</li>
          <li class="flex items-center gap-2 text-gray-400"><span>&#8212;</span> Team collaboration</li>
        </ul>
        <a href="contact.html" class="block text-center py-2.5 border border-gray-300 dark:border-gray-600 rounded-xl text-sm font-semibold hover:border-primary-500 hover:text-primary-500 transition-colors">Get Started Free</a>
      </div>
      <div class="reveal relative bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-2 border-primary-500 rounded-2xl p-6 flex flex-col gap-3">
        <div class="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white text-xs font-bold px-4 py-1 rounded-full">Most Popular</div>
        <div class="text-xs font-bold uppercase tracking-widest text-primary-500">Pro</div>
        <div class="text-4xl font-extrabold">
          <span x-text="yearly ? '$39' : '$49'">$49</span><span class="text-base font-normal text-gray-500">/mo</span>
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400">For growing teams that need more power and flexibility.</p>
        <ul class="space-y-2 text-sm flex-1">
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Unlimited projects</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> 100GB storage</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Priority support</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Advanced analytics</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Custom domains</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Team collaboration</li>
          <li class="flex items-center gap-2 text-gray-400"><span>&#8212;</span> Dedicated support</li>
        </ul>
        <a href="contact.html" class="block text-center py-2.5 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl text-sm font-semibold hover:opacity-90">Start Pro Trial</a>
      </div>
      <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 flex flex-col gap-3">
        <div class="text-xs font-bold uppercase tracking-widest text-gray-500">Enterprise</div>
        <div class="text-4xl font-extrabold">Custom</div>
        <p class="text-sm text-gray-500 dark:text-gray-400">Tailored solutions for large organizations with complex needs.</p>
        <ul class="space-y-2 text-sm flex-1">
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Everything in Pro</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Unlimited storage</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Dedicated support</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> SLA guarantee</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Custom contracts</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> On-premise option</li>
          <li class="flex items-center gap-2 text-gray-700 dark:text-gray-300"><span class="text-primary-500">&#10003;</span> Security audit</li>
        </ul>
        <a href="contact.html" class="block text-center py-2.5 border border-gray-300 dark:border-gray-600 rounded-xl text-sm font-semibold hover:border-primary-500 hover:text-primary-500 transition-colors">Contact Sales</a>
      </div>
    </div>
    <div class="max-w-3xl mx-auto" x-data="{ open: null }">
      <h2 class="text-2xl font-bold text-center mb-8">Pricing <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">FAQ</span></h2>
      <div class="space-y-3">
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===0 ? 'border-primary-500' : ''">
          <button @click="open = open===0 ? null : 0" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">Can I change plans at any time?<span class="text-primary-500 text-lg" x-text="open===0 ? '&#8722;' : '&#43;'">+</span></button>
          <div x-show="open===0" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately and are prorated.</div>
        </div>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===1 ? 'border-primary-500' : ''">
          <button @click="open = open===1 ? null : 1" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">Is there a free trial?<span class="text-primary-500 text-lg" x-text="open===1 ? '&#8722;' : '&#43;'">+</span></button>
          <div x-show="open===1" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">Yes! The Pro plan comes with a 14-day free trial. No credit card required to start.</div>
        </div>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===2 ? 'border-primary-500' : ''">
          <button @click="open = open===2 ? null : 2" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">What payment methods do you accept?<span class="text-primary-500 text-lg" x-text="open===2 ? '&#8722;' : '&#43;'">+</span></button>
          <div x-show="open===2" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">We accept all major credit cards, PayPal, and bank transfers for annual plans. Enterprise customers can also pay by invoice.</div>
        </div>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===3 ? 'border-primary-500' : ''">
          <button @click="open = open===3 ? null : 3" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">What happens when I cancel?<span class="text-primary-500 text-lg" x-text="open===3 ? '&#8722;' : '&#43;'">+</span></button>
          <div x-show="open===3" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">You can cancel anytime. Your account remains active until the end of the billing period. We do not offer refunds for partial months.</div>
        </div>
      </div>
    </div>
  </div>
</section>"""

_SP2_TEAM_BODY = """﻿<section class="py-20 px-4 sm:px-6 text-center bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-b border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto">
    <h1 class="text-4xl sm:text-5xl font-extrabold mb-4">Meet the <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Team</span></h1>
    <p class="text-gray-500 dark:text-gray-400 text-lg">The talented people behind NovaTech's mission to make great infrastructure accessible to everyone.</p>
  </div>
</section>
<section class="py-20 px-4 sm:px-6">
  <div class="max-w-6xl mx-auto grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
    <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center hover:border-primary-500 hover:-translate-y-1 transition-all">
      <div class="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">AK</div>
      <h3 class="font-semibold text-lg">Alex Kim</h3>
      <p class="text-xs text-primary-500 font-semibold mb-3">CEO &amp; Co-Founder</p>
      <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed mb-4">Former Google engineer with 15 years building distributed systems. Passionate about developer experience.</p>
      <div class="flex gap-2 justify-center">
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="Twitter">&#120143;</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="LinkedIn">in</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="GitHub">GH</a>
      </div>
    </div>
    <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center hover:border-primary-500 hover:-translate-y-1 transition-all">
      <div class="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">SR</div>
      <h3 class="font-semibold text-lg">Sofia Reyes</h3>
      <p class="text-xs text-primary-500 font-semibold mb-3">CTO &amp; Co-Founder</p>
      <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed mb-4">PhD in Computer Science from MIT. Expert in distributed systems and cloud architecture.</p>
      <div class="flex gap-2 justify-center">
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="Twitter">&#120143;</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="LinkedIn">in</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="GitHub">GH</a>
      </div>
    </div>
    <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center hover:border-primary-500 hover:-translate-y-1 transition-all">
      <div class="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">JL</div>
      <h3 class="font-semibold text-lg">James Liu</h3>
      <p class="text-xs text-primary-500 font-semibold mb-3">VP Engineering</p>
      <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed mb-4">Led engineering teams at Stripe and Cloudflare. Obsessed with reliability and performance.</p>
      <div class="flex gap-2 justify-center">
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="Twitter">&#120143;</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="LinkedIn">in</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="GitHub">GH</a>
      </div>
    </div>
    <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center hover:border-primary-500 hover:-translate-y-1 transition-all">
      <div class="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">MP</div>
      <h3 class="font-semibold text-lg">Maya Patel</h3>
      <p class="text-xs text-primary-500 font-semibold mb-3">Head of Design</p>
      <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed mb-4">Award-winning designer with a background in HCI. Believes great UX is invisible.</p>
      <div class="flex gap-2 justify-center">
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="Twitter">&#120143;</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="LinkedIn">in</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="GitHub">GH</a>
      </div>
    </div>
    <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center hover:border-primary-500 hover:-translate-y-1 transition-all">
      <div class="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">DW</div>
      <h3 class="font-semibold text-lg">David Wang</h3>
      <p class="text-xs text-primary-500 font-semibold mb-3">Head of Security</p>
      <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed mb-4">Former NSA security researcher. Leads our SOC 2 compliance and zero-trust initiatives.</p>
      <div class="flex gap-2 justify-center">
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="Twitter">&#120143;</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="LinkedIn">in</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="GitHub">GH</a>
      </div>
    </div>
    <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center hover:border-primary-500 hover:-translate-y-1 transition-all">
      <div class="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">LM</div>
      <h3 class="font-semibold text-lg">Laura Martinez</h3>
      <p class="text-xs text-primary-500 font-semibold mb-3">Head of Product</p>
      <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed mb-4">Product leader who shipped features used by millions at Notion and Linear. Customer-obsessed.</p>
      <div class="flex gap-2 justify-center">
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="Twitter">&#120143;</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="LinkedIn">in</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="GitHub">GH</a>
      </div>
    </div>
    <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center hover:border-primary-500 hover:-translate-y-1 transition-all">
      <div class="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">RO</div>
      <h3 class="font-semibold text-lg">Ryan O'Brien</h3>
      <p class="text-xs text-primary-500 font-semibold mb-3">Head of Sales</p>
      <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed mb-4">Built and scaled sales teams at Datadog and PagerDuty. Loves helping customers succeed.</p>
      <div class="flex gap-2 justify-center">
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="Twitter">&#120143;</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="LinkedIn">in</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="GitHub">GH</a>
      </div>
    </div>
    <div class="reveal bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 text-center hover:border-primary-500 hover:-translate-y-1 transition-all">
      <div class="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">ZC</div>
      <h3 class="font-semibold text-lg">Zara Chen</h3>
      <p class="text-xs text-primary-500 font-semibold mb-3">Lead AI Engineer</p>
      <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed mb-4">ML researcher turned engineer. Leads our AI platform and model inference infrastructure.</p>
      <div class="flex gap-2 justify-center">
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="Twitter">&#120143;</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="LinkedIn">in</a>
        <a href="#" class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-primary-500 hover:text-white flex items-center justify-center text-xs transition-colors" aria-label="GitHub">GH</a>
      </div>
    </div>
  </div>
</section>
<section class="py-20 px-4 sm:px-6 bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-t border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto text-center">
    <h2 class="text-3xl font-bold mb-4">Join Our <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Team</span></h2>
    <p class="text-gray-500 dark:text-gray-400 mb-8">We are always looking for talented people who share our passion for building great software.</p>
    <a href="contact.html" class="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-full hover:opacity-90 transition-opacity shadow-lg">View Open Positions</a>
  </div>
</section>"""

_SP2_FAQ_BODY = """﻿<section class="py-20 px-4 sm:px-6 text-center bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-b border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto">
    <h1 class="text-4xl sm:text-5xl font-extrabold mb-4">Frequently Asked <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Questions</span></h1>
    <p class="text-gray-500 dark:text-gray-400 text-lg">Everything you need to know about NovaTech.</p>
  </div>
</section>
<section class="py-20 px-4 sm:px-6" x-data="{ cat: 'all', open: null }">
  <div class="max-w-3xl mx-auto">
    <div class="flex flex-wrap gap-3 justify-center mb-10">
      <button @click="cat='all'; open=null" :class="cat==='all' ? 'bg-primary-500 text-white border-primary-500' : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400'" class="px-4 py-1.5 rounded-full text-sm font-medium border transition-all">All</button>
      <button @click="cat='general'; open=null" :class="cat==='general' ? 'bg-primary-500 text-white border-primary-500' : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400'" class="px-4 py-1.5 rounded-full text-sm font-medium border transition-all">General</button>
      <button @click="cat='billing'; open=null" :class="cat==='billing' ? 'bg-primary-500 text-white border-primary-500' : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400'" class="px-4 py-1.5 rounded-full text-sm font-medium border transition-all">Billing</button>
      <button @click="cat='technical'; open=null" :class="cat==='technical' ? 'bg-primary-500 text-white border-primary-500' : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400'" class="px-4 py-1.5 rounded-full text-sm font-medium border transition-all">Technical</button>
      <button @click="cat='security'; open=null" :class="cat==='security' ? 'bg-primary-500 text-white border-primary-500' : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400'" class="px-4 py-1.5 rounded-full text-sm font-medium border transition-all">Security</button>
    </div>
    <div class="space-y-3">
      <div x-show="cat==='all' || cat==='general'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===0 ? 'border-primary-500' : ''">
        <button @click="open = open===0 ? null : 0" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">What is NovaTech?<span class="text-primary-500 text-lg" x-text="open===0 ? '&#8722;' : '&#43;'">+</span></button>
        <div x-show="open===0" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">NovaTech is a cloud infrastructure platform that helps developers and businesses deploy, scale, and manage their applications with ease. We handle the complexity so you can focus on building.</div>
      </div>
      <div x-show="cat==='all' || cat==='general'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===1 ? 'border-primary-500' : ''">
        <button @click="open = open===1 ? null : 1" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">Who is NovaTech for?<span class="text-primary-500 text-lg" x-text="open===1 ? '&#8722;' : '&#43;'">+</span></button>
        <div x-show="open===1" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">NovaTech is built for developers, startups, and enterprises of all sizes. Whether you are a solo developer or a Fortune 500 company, our platform scales to meet your needs.</div>
      </div>
      <div x-show="cat==='all' || cat==='general'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===2 ? 'border-primary-500' : ''">
        <button @click="open = open===2 ? null : 2" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">How do I get started?<span class="text-primary-500 text-lg" x-text="open===2 ? '&#8722;' : '&#43;'">+</span></button>
        <div x-show="open===2" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">Sign up for a free account at novatech.io. No credit card required. You can deploy your first project in under 5 minutes with our guided setup wizard.</div>
      </div>
      <div x-show="cat==='all' || cat==='billing'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===3 ? 'border-primary-500' : ''">
        <button @click="open = open===3 ? null : 3" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">Can I cancel my subscription anytime?<span class="text-primary-500 text-lg" x-text="open===3 ? '&#8722;' : '&#43;'">+</span></button>
        <div x-show="open===3" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">Yes, you can cancel at any time from your account settings. Your subscription remains active until the end of the current billing period.</div>
      </div>
      <div x-show="cat==='all' || cat==='billing'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===4 ? 'border-primary-500' : ''">
        <button @click="open = open===4 ? null : 4" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">Do you offer refunds?<span class="text-primary-500 text-lg" x-text="open===4 ? '&#8722;' : '&#43;'">+</span></button>
        <div x-show="open===4" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">We offer a 30-day money-back guarantee for new Pro subscribers. Enterprise customers should contact sales for refund policies.</div>
      </div>
      <div x-show="cat==='all' || cat==='billing'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===5 ? 'border-primary-500' : ''">
        <button @click="open = open===5 ? null : 5" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">What payment methods are accepted?<span class="text-primary-500 text-lg" x-text="open===5 ? '&#8722;' : '&#43;'">+</span></button>
        <div x-show="open===5" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">We accept Visa, Mastercard, American Express, PayPal, and bank transfers for annual plans. Enterprise customers can pay by invoice.</div>
      </div>
      <div x-show="cat==='all' || cat==='technical'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===6 ? 'border-primary-500' : ''">
        <button @click="open = open===6 ? null : 6" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">What programming languages do you support?<span class="text-primary-500 text-lg" x-text="open===6 ? '&#8722;' : '&#43;'">+</span></button>
        <div x-show="open===6" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">NovaTech supports all major languages including Node.js, Python, Go, Ruby, Java, PHP, and more. If it runs in a container, it runs on NovaTech.</div>
      </div>
      <div x-show="cat==='all' || cat==='technical'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===7 ? 'border-primary-500' : ''">
        <button @click="open = open===7 ? null : 7" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">What is your uptime SLA?<span class="text-primary-500 text-lg" x-text="open===7 ? '&#8722;' : '&#43;'">+</span></button>
        <div x-show="open===7" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">We guarantee 99.9% uptime for all plans. Enterprise customers get a 99.99% SLA with financial credits if we fall short.</div>
      </div>
      <div x-show="cat==='all' || cat==='technical'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===8 ? 'border-primary-500' : ''">
        <button @click="open = open===8 ? null : 8" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">Can I migrate from another provider?<span class="text-primary-500 text-lg" x-text="open===8 ? '&#8722;' : '&#43;'">+</span></button>
        <div x-show="open===8" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">Yes! We have migration guides for AWS, GCP, Azure, Heroku, and more. Our team can also assist with complex migrations at no extra cost.</div>
      </div>
      <div x-show="cat==='all' || cat==='security'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===9 ? 'border-primary-500' : ''">
        <button @click="open = open===9 ? null : 9" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">Is NovaTech SOC 2 certified?<span class="text-primary-500 text-lg" x-text="open===9 ? '&#8722;' : '&#43;'">+</span></button>
        <div x-show="open===9" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">Yes, NovaTech is SOC 2 Type II certified. We undergo annual audits and our security reports are available to enterprise customers under NDA.</div>
      </div>
      <div x-show="cat==='all' || cat==='security'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===10 ? 'border-primary-500' : ''">
        <button @click="open = open===10 ? null : 10" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">How is my data encrypted?<span class="text-primary-500 text-lg" x-text="open===10 ? '&#8722;' : '&#43;'">+</span></button>
        <div x-show="open===10" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">All data is encrypted at rest using AES-256 and in transit using TLS 1.3. We use hardware security modules (HSMs) for key management.</div>
      </div>
      <div x-show="cat==='all' || cat==='security'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden" :class="open===11 ? 'border-primary-500' : ''">
        <button @click="open = open===11 ? null : 11" class="w-full flex justify-between items-center px-5 py-4 text-left font-medium text-sm">Do you support GDPR compliance?<span class="text-primary-500 text-lg" x-text="open===11 ? '&#8722;' : '&#43;'">+</span></button>
        <div x-show="open===11" x-cloak class="px-5 pb-4 text-sm text-gray-500 dark:text-gray-400">Yes, NovaTech is fully GDPR compliant. We offer EU data residency, data processing agreements (DPAs), and tools to help you manage user data requests.</div>
      </div>
    </div>
  </div>
</section>"""

_SP2_TESTIMONIALS_BODY = """﻿<section class="py-20 px-4 sm:px-6 text-center bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-b border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto">
    <h1 class="text-4xl sm:text-5xl font-extrabold mb-4">What Our <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">Customers Say</span></h1>
    <p class="text-gray-500 dark:text-gray-400 text-lg">Real feedback from real teams building with NovaTech every day.</p>
  </div>
</section>
<section class="py-20 px-4 sm:px-6">
  <div class="max-w-6xl mx-auto">
    <div class="flex flex-col sm:flex-row items-center gap-8 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-8 mb-14 reveal">
      <div class="text-center sm:text-left">
        <div class="text-6xl font-extrabold text-primary-500 leading-none">4.9</div>
        <div class="text-yellow-400 text-2xl my-1">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <div class="text-sm text-gray-500 dark:text-gray-400">Average rating</div>
      </div>
      <div class="w-px h-16 bg-gray-200 dark:bg-gray-700 hidden sm:block"></div>
      <div class="grid grid-cols-3 gap-6 flex-1 text-center">
        <div><div class="text-2xl font-bold text-primary-500">1,200+</div><div class="text-xs text-gray-500 dark:text-gray-400">Reviews</div></div>
        <div><div class="text-2xl font-bold text-primary-500">98%</div><div class="text-xs text-gray-500 dark:text-gray-400">Would recommend</div></div>
        <div><div class="text-2xl font-bold text-primary-500">10K+</div><div class="text-xs text-gray-500 dark:text-gray-400">Happy customers</div></div>
      </div>
    </div>
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div class="reveal relative bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="absolute top-4 right-5 text-4xl text-primary-500 opacity-20 font-serif leading-none">"</div>
        <div class="text-yellow-400 mb-3">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <blockquote class="text-gray-600 dark:text-gray-300 italic text-sm leading-relaxed mb-5">"NovaTech cut our deployment time by 80%. The auto-scaling alone saved us thousands in infrastructure costs. Absolutely game-changing."</blockquote>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">SC</div>
          <div><strong class="block text-sm">Sarah Chen</strong><span class="text-xs text-gray-500 dark:text-gray-400">CTO, TechFlow Inc.</span></div>
        </div>
      </div>
      <div class="reveal relative bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="absolute top-4 right-5 text-4xl text-primary-500 opacity-20 font-serif leading-none">"</div>
        <div class="text-yellow-400 mb-3">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <blockquote class="text-gray-600 dark:text-gray-300 italic text-sm leading-relaxed mb-5">"The best developer experience I have had in 10 years. The documentation is excellent and support is incredibly fast. Highly recommend."</blockquote>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">MJ</div>
          <div><strong class="block text-sm">Marcus Johnson</strong><span class="text-xs text-gray-500 dark:text-gray-400">Lead Engineer, StartupX</span></div>
        </div>
      </div>
      <div class="reveal relative bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="absolute top-4 right-5 text-4xl text-primary-500 opacity-20 font-serif leading-none">"</div>
        <div class="text-yellow-400 mb-3">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <blockquote class="text-gray-600 dark:text-gray-300 italic text-sm leading-relaxed mb-5">"We migrated 50+ microservices to NovaTech in a weekend. Zero downtime, zero issues. The team support was outstanding throughout."</blockquote>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">AP</div>
          <div><strong class="block text-sm">Aisha Patel</strong><span class="text-xs text-gray-500 dark:text-gray-400">VP Engineering, ScaleUp</span></div>
        </div>
      </div>
      <div class="reveal relative bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="absolute top-4 right-5 text-4xl text-primary-500 opacity-20 font-serif leading-none">"</div>
        <div class="text-yellow-400 mb-3">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <blockquote class="text-gray-600 dark:text-gray-300 italic text-sm leading-relaxed mb-5">"The security features are enterprise-grade. SOC 2 compliance was a breeze with NovaTech's built-in tools. Our auditors were impressed."</blockquote>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">TN</div>
          <div><strong class="block text-sm">Tom Nakamura</strong><span class="text-xs text-gray-500 dark:text-gray-400">CISO, FinTech Corp</span></div>
        </div>
      </div>
      <div class="reveal relative bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="absolute top-4 right-5 text-4xl text-primary-500 opacity-20 font-serif leading-none">"</div>
        <div class="text-yellow-400 mb-3">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <blockquote class="text-gray-600 dark:text-gray-300 italic text-sm leading-relaxed mb-5">"Switched from AWS and cut our cloud bill by 40%. The pricing is transparent and the performance is actually better. Could not be happier."</blockquote>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">EW</div>
          <div><strong class="block text-sm">Emma Wilson</strong><span class="text-xs text-gray-500 dark:text-gray-400">CTO, GrowthLabs</span></div>
        </div>
      </div>
      <div class="reveal relative bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:border-primary-500 hover:-translate-y-1 transition-all">
        <div class="absolute top-4 right-5 text-4xl text-primary-500 opacity-20 font-serif leading-none">"</div>
        <div class="text-yellow-400 mb-3">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <blockquote class="text-gray-600 dark:text-gray-300 italic text-sm leading-relaxed mb-5">"The AI insights feature is incredible. It caught a performance regression before our users noticed. That alone is worth the subscription price."</blockquote>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">RB</div>
          <div><strong class="block text-sm">Raj Bhatia</strong><span class="text-xs text-gray-500 dark:text-gray-400">Founder, DevTools.io</span></div>
        </div>
      </div>
    </div>
  </div>
</section>
<section class="py-20 px-4 sm:px-6 bg-gradient-to-br from-primary-500/10 to-secondary-500/5 border-t border-gray-200 dark:border-gray-700">
  <div class="max-w-3xl mx-auto text-center">
    <h2 class="text-3xl font-bold mb-4">Join <span class="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">10,000+ Teams</span></h2>
    <p class="text-gray-500 dark:text-gray-400 mb-8">Start your free trial today. No credit card required.</p>
    <div class="flex flex-wrap gap-4 justify-center">
      <a href="contact.html" class="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-full hover:opacity-90 transition-opacity shadow-lg">Start Free Trial</a>
      <a href="pricing.html" class="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold rounded-full hover:border-primary-500 hover:text-primary-500 transition-colors">View Pricing &#8594;</a>
    </div>
  </div>
</section>"""

_SP2_CSS = """:root { --primary: PRIMARY_COLOR; --secondary: SECONDARY_COLOR; }
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

_SP2_JS = """// Active nav link detection
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


def _sp2_head(name: str, primary: str, secondary: str, font: str, page_title: str) -> str:
    """Generate the HTML head for a Static Pro page."""
    font_url = font.replace(' ', '+')
    dark = _sp2_darken(primary)
    return (
        f'<!DOCTYPE html>\n'
        f'<html lang="en" x-data="{{ dark: localStorage.getItem(\'dark\')===\'true\', mobileOpen: false }}" :class="dark ? \'dark\' : \'\'" class="scroll-smooth">\n'
        f'<head>\n'
        f'  <meta charset="UTF-8"/>\n'
        f'  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>\n'
        f'  <title>{name} &mdash; {page_title}</title>\n'
        f'  <script src="https://cdn.tailwindcss.com"></script>\n'
        f'  <script>\n'
        f'    tailwind.config = {{\n'
        f'      darkMode: \'class\',\n'
        f'      theme: {{ extend: {{ colors: {{ primary: {{ 50:\'#f5f3ff\', 500:\'{primary}\', 600:\'{dark}\' }}, secondary: {{ 500:\'{secondary}\' }} }}, fontFamily: {{ sans: [\'{font}\',\'system-ui\',\'sans-serif\'] }} }} }}\n'
        f'    }}\n'
        f'  </script>\n'
        f'  <link rel="preconnect" href="https://fonts.googleapis.com"/>\n'
        f'  <link href="https://fonts.googleapis.com/css2?family={font_url}:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>\n'
        f'  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>\n'
        f'  <link rel="stylesheet" href="style.css"/>\n'
        f'</head>\n'
        f'<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white font-sans antialiased">\n'
    )


def _sp2_nav(name: str) -> str:
    """Generate the navbar for a Static Pro page."""
    return (
        f'<nav id="navbar" class="sticky top-0 z-50 bg-white/95 dark:bg-gray-900/95 backdrop-blur border-b border-gray-200 dark:border-gray-800 transition-shadow">\n'
        f'  <div class="max-w-6xl mx-auto px-4 sm:px-6 flex items-center justify-between h-16">\n'
        f'    <a href="index.html" class="text-xl font-bold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">&#9889; {name}</a>\n'
        '    <ul class="hidden md:flex items-center gap-6 list-none">\n'
        '      <li><a href="index.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Home</a></li>\n'
        '      <li><a href="about.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">About</a></li>\n'
        '      <li><a href="services.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Services</a></li>\n'
        '      <li><a href="portfolio.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Portfolio</a></li>\n'
        '      <li><a href="blog.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Blog</a></li>\n'
        '      <li><a href="contact.html" data-nav class="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition-colors">Contact</a></li>\n'
        '      <li><a href="pricing.html" data-nav class="text-sm font-medium bg-gradient-to-r from-primary-500 to-secondary-500 text-white px-4 py-1.5 rounded-full hover:opacity-90">Pricing</a></li>\n'
        '    </ul>\n'
        '    <div class="flex items-center gap-3">\n'
        '      <button @click="dark=!dark; localStorage.setItem(\'dark\', dark)" class="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" aria-label="Toggle dark mode">\n'
        '        <svg x-show="!dark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>\n'
        '        <svg x-show="dark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>\n'
        '      </button>\n'
        '      <button @click="mobileOpen=!mobileOpen" class="md:hidden p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" aria-label="Toggle menu">\n'
        '        <svg x-show="!mobileOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>\n'
        '        <svg x-show="mobileOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>\n'
        '      </button>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div x-show="mobileOpen" x-cloak x-transition class="md:hidden border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-4 py-3 flex flex-col gap-3">\n'
        '    <a href="index.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Home</a>\n'
        '    <a href="about.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">About</a>\n'
        '    <a href="services.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Services</a>\n'
        '    <a href="portfolio.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Portfolio</a>\n'
        '    <a href="blog.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Blog</a>\n'
        '    <a href="contact.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-500">Contact</a>\n'
        '    <a href="pricing.html" data-nav @click="mobileOpen=false" class="text-sm font-medium text-primary-500 font-semibold">Pricing</a>\n'
        '  </div>\n'
        '</nav>\n'
    )


def _sp2_footer(name: str) -> str:
    """Generate the footer for a Static Pro page."""
    email = name.lower().replace(' ', '') + '.io'
    return (
        f'<footer class="bg-gray-900 dark:bg-gray-950 text-gray-400 pt-14 pb-6">\n'
        f'  <div class="max-w-6xl mx-auto px-4 sm:px-6">\n'
        f'    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-10">\n'
        f'      <div>\n'
        f'        <a href="index.html" class="text-xl font-bold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">&#9889; {name}</a>\n'
        '        <p class="mt-3 text-sm leading-relaxed">Building the future with cutting-edge technology. Trusted by teams worldwide.</p>\n'
        '        <div class="flex gap-3 mt-4">\n'
        '          <a href="#" class="w-8 h-8 rounded-lg bg-gray-800 hover:bg-primary-500 flex items-center justify-center transition-colors text-xs" aria-label="Twitter">&#120143;</a>\n'
        '          <a href="#" class="w-8 h-8 rounded-lg bg-gray-800 hover:bg-primary-500 flex items-center justify-center transition-colors text-xs" aria-label="LinkedIn">in</a>\n'
        '          <a href="#" class="w-8 h-8 rounded-lg bg-gray-800 hover:bg-primary-500 flex items-center justify-center transition-colors text-xs" aria-label="GitHub">GH</a>\n'
        '        </div>\n'
        '      </div>\n'
        '      <div><h4 class="text-white text-sm font-semibold mb-4">Pages</h4><ul class="space-y-2 text-sm">\n'
        '        <li><a href="index.html" class="hover:text-primary-500 transition-colors">Home</a></li>\n'
        '        <li><a href="about.html" class="hover:text-primary-500 transition-colors">About</a></li>\n'
        '        <li><a href="services.html" class="hover:text-primary-500 transition-colors">Services</a></li>\n'
        '        <li><a href="portfolio.html" class="hover:text-primary-500 transition-colors">Portfolio</a></li>\n'
        '        <li><a href="blog.html" class="hover:text-primary-500 transition-colors">Blog</a></li>\n'
        '      </ul></div>\n'
        '      <div><h4 class="text-white text-sm font-semibold mb-4">More</h4><ul class="space-y-2 text-sm">\n'
        '        <li><a href="pricing.html" class="hover:text-primary-500 transition-colors">Pricing</a></li>\n'
        '        <li><a href="team.html" class="hover:text-primary-500 transition-colors">Team</a></li>\n'
        '        <li><a href="faq.html" class="hover:text-primary-500 transition-colors">FAQ</a></li>\n'
        '        <li><a href="testimonials.html" class="hover:text-primary-500 transition-colors">Testimonials</a></li>\n'
        '        <li><a href="contact.html" class="hover:text-primary-500 transition-colors">Contact</a></li>\n'
        '      </ul></div>\n'
        f'      <div><h4 class="text-white text-sm font-semibold mb-4">Contact</h4><ul class="space-y-2 text-sm">\n'
        f'        <li>hello@{email}</li>\n'
        '        <li>+1 (555) 000-1234</li>\n'
        '        <li>123 Tech Ave, SF, CA</li>\n'
        '        <li>Mon-Fri 9am-6pm PST</li>\n'
        '      </ul></div>\n'
        '    </div>\n'
        f'    <div class="border-t border-gray-800 pt-6 flex flex-col sm:flex-row justify-between items-center gap-2 text-xs">\n'
        f'      <span>&copy; 2025 {name}. All rights reserved.</span>\n'
        '      <span>Made with &#10084;&#65039; for developers</span>\n'
        '    </div>\n'
        '  </div>\n'
        '</footer>\n'
        '<script src="script.js"></script>\n'
        '</body>\n'
        '</html>\n'
    )


def _sp2_page(name: str, primary: str, secondary: str, font: str, page_title: str, body: str) -> str:
    """Assemble a complete Static Pro HTML page."""
    return (
        _sp2_head(name, primary, secondary, font, page_title)
        + _sp2_nav(name)
        + body
        + _sp2_footer(name)
    )


def _gen_static(config: dict) -> dict:
    """Generate a Static Pro 10-page website with Tailwind CSS + Alpine.js."""
    name      = _c(config, 'site_name', 'My Website')
    primary   = _c(config, 'primary_color', '#6c63ff')
    secondary = _c(config, 'secondary_color', '#f50057')
    font      = _c(config, 'font', 'Inter')

    def pg(title, body_const):
        return _sp2_page(name, primary, secondary, font, title, body_const)

    css = _SP2_CSS.replace('PRIMARY_COLOR', primary).replace('SECONDARY_COLOR', secondary)

    return {
        'index.html':        pg('Home',         _SP2_INDEX_BODY),
        'about.html':        pg('About',        _SP2_ABOUT_BODY),
        'services.html':     pg('Services',     _SP2_SERVICES_BODY),
        'portfolio.html':    pg('Portfolio',    _SP2_PORTFOLIO_BODY),
        'blog.html':         pg('Blog',         _SP2_BLOG_BODY),
        'contact.html':      pg('Contact',      _SP2_CONTACT_BODY),
        'pricing.html':      pg('Pricing',      _SP2_PRICING_BODY),
        'team.html':         pg('Team',         _SP2_TEAM_BODY),
        'faq.html':          pg('FAQ',          _SP2_FAQ_BODY),
        'testimonials.html': pg('Testimonials', _SP2_TESTIMONIALS_BODY),
        'style.css':         css,
        'script.js':         _SP2_JS,
        'README.txt':        f'{name}\nOpen index.html in your browser.\nBuilt with Static Pro generator.\n',
    }
