"""
_pages.py — Page generator functions for Website Builder System
Each function assembles sections + navbar + footer into a complete HTML page.
"""
from build import (
    _page_head, _navbar, _footer,
    _page_hero, _section_stats, _section_features,
    _section_testimonials, _section_cta, _section_page_hero,
)


def generate_home(cfg: dict) -> str:
    anim = cfg["features"]["animations"]
    rv   = "reveal" if anim else ""
    name = cfg["site_name"]

    return (
        _page_head(cfg, "Home", cfg["description"])
        + _navbar(cfg, "home")
        + _page_hero(cfg)
        + _section_stats(cfg)
        + _section_features(cfg)
        + _section_testimonials(cfg)
        + _section_cta(cfg)
        + _footer(cfg)
    )


def generate_about(cfg: dict) -> str:
    anim = cfg["features"]["animations"]
    rv   = "reveal" if anim else ""
    rvl  = "reveal-left" if anim else ""
    rvr  = "reveal-right" if anim else ""
    name = cfg["site_name"]
    team = cfg["content"].get("team", [])[:4]

    team_cards = ""
    for m in team:
        team_cards += f"""<div class="{rv} card-hover card-gradient-border bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl p-6 text-center">
      <div class="w-16 h-16 rounded-full btn-gradient flex items-center justify-center text-white font-black text-xl mx-auto mb-3" aria-hidden="true">{m['initials']}</div>
      <div class="font-bold text-sm dark:text-white">{m['name']}</div>
      <div class="text-xs text-primary mt-0.5">{m['role']}</div>
    </div>\n    """

    values = [
        ("🎯", "Customer Obsession",    "Every feature we build starts with a customer problem. We listen, iterate, and ship fast."),
        ("🔬", "Engineering Excellence","We hold ourselves to the highest technical standards. Clean code, thorough testing."),
        ("🌍", "Radical Transparency",  "We share our roadmap, our mistakes, and our learnings openly. Trust is built through honesty."),
        ("⚡", "Move Fast",             "Speed matters. We ship weekly, learn from real users, and iterate quickly."),
        ("🤝", "Inclusive Culture",     "Great ideas come from diverse perspectives. We actively build a team that reflects the world."),
        ("🌱", "Long-term Thinking",    "We optimize for decades, not quarters. Sustainable growth and a healthy team."),
    ]
    val_cards = ""
    for icon, title, desc in values:
        val_cards += f"""<article class="{rv} card-hover card-gradient-border bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
      <div class="text-2xl mb-3" aria-hidden="true">{icon}</div>
      <h3 class="font-bold mb-2 dark:text-white">{title}</h3>
      <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{desc}</p>
    </article>\n    """

    body = f"""
{_section_page_hero(cfg, f'About <span class="gradient-text">{name}</span>',
    "We're a team of engineers, designers, and dreamers on a mission to make great software accessible to every team.")}

<section class="py-24 px-4">
  <div class="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-14 items-center">
    <div class="{rvl}">
      <span class="text-primary text-sm font-semibold uppercase tracking-wider">Who We Are</span>
      <h2 class="text-3xl md:text-4xl font-black mt-2 mb-5 dark:text-white">Our <span class="gradient-text">Story</span></h2>
      <p class="text-gray-500 dark:text-gray-400 leading-relaxed mb-4">{name} was founded in 2019 by a group of engineers frustrated with the complexity of modern infrastructure. We believed that deploying and scaling software should be simple, fast, and reliable.</p>
      <p class="text-gray-500 dark:text-gray-400 leading-relaxed mb-6">Starting from a small apartment in San Francisco, we built the first version of our platform in 3 months. Today, we serve over 10,000 teams across 80 countries.</p>
      <a href="contact.html" class="btn-gradient px-6 py-3 rounded-full font-bold text-sm inline-block focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:ring-offset-2">Work With Us →</a>
    </div>
    <div class="{rvr} grid grid-cols-2 gap-4">
      <div class="bg-primary-10 border border-primary-15 rounded-2xl p-5 text-center card-hover"><div class="text-3xl font-black text-primary mb-1">80+</div><div class="text-sm text-gray-500 dark:text-gray-400">Countries</div></div>
      <div class="bg-pink-50 dark:bg-pink-900/20 border border-pink-100 dark:border-pink-800 rounded-2xl p-5 text-center card-hover"><div class="text-3xl font-black mb-1" style="color:var(--secondary)">50+</div><div class="text-sm text-gray-500 dark:text-gray-400">Team Members</div></div>
      <div class="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800 rounded-2xl p-5 text-center card-hover"><div class="text-3xl font-black text-emerald-600 mb-1">$40M</div><div class="text-sm text-gray-500 dark:text-gray-400">Series B</div></div>
      <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-800 rounded-2xl p-5 text-center card-hover"><div class="text-3xl font-black text-amber-500 mb-1">4.9★</div><div class="text-sm text-gray-500 dark:text-gray-400">G2 Rating</div></div>
    </div>
  </div>
</section>

<section class="py-24 px-4 bg-gray-50 dark:bg-gray-900 border-y border-gray-100 dark:border-gray-800">
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-16 {rv}">
      <span class="text-primary text-sm font-semibold uppercase tracking-wider">Principles</span>
      <h2 class="text-4xl font-black mt-2 dark:text-white">Our <span class="gradient-text">Values</span></h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">{val_cards}</div>
  </div>
</section>
"""

    if team:
        body += f"""
<section class="py-24 px-4">
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-16 {rv}">
      <span class="text-primary text-sm font-semibold uppercase tracking-wider">People</span>
      <h2 class="text-4xl font-black mt-2 dark:text-white">Meet the <span class="gradient-text">Team</span></h2>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-6">{team_cards}</div>
    <div class="text-center mt-10 {rv}">
      <a href="team.html" class="btn-outline-primary px-6 py-2.5 rounded-full text-sm font-bold focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:ring-offset-2">Meet the Full Team →</a>
    </div>
  </div>
</section>"""

    return _page_head(cfg, "About") + _navbar(cfg, "about") + body + _section_cta(cfg) + _footer(cfg)


def generate_services(cfg: dict) -> str:
    anim     = cfg["features"]["animations"]
    rv       = "reveal" if anim else ""
    services = cfg["content"].get("services", [])

    cards = ""
    for svc in services:
        feats = "".join(f'<li class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400"><span class="text-primary font-bold" aria-hidden="true">✓</span>{f}</li>' for f in svc.get("features", []))
        cards += f"""<article class="{rv} card-hover card-gradient-border bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl p-7">
      <div class="w-12 h-12 rounded-xl bg-primary-10 flex items-center justify-center text-2xl mb-5" aria-hidden="true">{svc['icon']}</div>
      <h2 class="font-black text-lg mb-2 dark:text-white">{svc['title']}</h2>
      <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed mb-4">{svc['desc']}</p>
      <ul class="space-y-1.5 mb-5" role="list">{feats}</ul>
      <a href="contact.html" class="text-primary text-sm font-semibold hover:underline focus:outline-none focus:ring-2 focus:ring-[var(--primary)] rounded">Learn more →</a>
    </article>\n    """

    steps = [("01","Sign Up","Create your account in seconds. No credit card required."),
             ("02","Connect","Link your repo. We detect your stack automatically."),
             ("03","Deploy","Push to main and your app is live globally in 30 seconds."),
             ("04","Scale","Traffic spikes? We handle it automatically.")]
    step_html = ""
    for num, title, desc in steps:
        step_html += f'<div class="{rv} text-center"><div class="text-4xl font-black gradient-text mb-3">{num}</div><h3 class="font-bold mb-2 dark:text-white">{title}</h3><p class="text-sm text-gray-500 dark:text-gray-400">{desc}</p></div>\n    '

    body = f"""
{_section_page_hero(cfg, f'Our <span class="gradient-text">Services</span>',
    "From cloud infrastructure to AI-powered tooling — everything your team needs to ship faster.")}
<section class="py-24 px-4">
  <div class="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">{cards}</div>
</section>
<section class="py-24 px-4 bg-gray-50 dark:bg-gray-900 border-y border-gray-100 dark:border-gray-800">
  <div class="max-w-5xl mx-auto">
    <div class="text-center mb-16 {rv}">
      <span class="text-primary text-sm font-semibold uppercase tracking-wider">How It Works</span>
      <h2 class="text-4xl font-black mt-2 dark:text-white">Get Started in <span class="gradient-text">Minutes</span></h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">{step_html}</div>
  </div>
</section>"""
    return _page_head(cfg, "Services") + _navbar(cfg, "services") + body + _section_cta(cfg) + _footer(cfg)


def generate_portfolio(cfg: dict) -> str:
    anim   = cfg["features"]["animations"]
    rv     = "reveal" if anim else ""
    pf     = cfg["features"]["portfolio_filter"]
    items  = cfg["content"].get("portfolio_items", [])

    cats = sorted(set(i["category"] for i in items))
    filter_btns = ""
    if pf:
        filter_btns = '<button @click="filter=\'all\'" :class="filter===\'all\'?\'btn-gradient\':\'btn-outline-primary\'" class="px-5 py-2 rounded-full text-sm font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-[var(--primary)]" :aria-pressed="(filter===\'all\').toString()">All</button>\n      '
        for cat in cats:
            filter_btns += f'<button @click="filter=\'{cat}\'" :class="filter===\'{cat}\'?\'btn-gradient\':\'btn-outline-primary\'" class="px-5 py-2 rounded-full text-sm font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-[var(--primary)]" :aria-pressed="(filter===\'{cat}\').toString()">{cat.title()}</button>\n      '

    cards = ""
    for it in items:
        show = f"filter==='all'||filter==='{it['category']}'" if pf else "true"
        cards += f"""<article x-show="{show}" x-transition class="group relative overflow-hidden rounded-2xl shadow-sm hover:shadow-xl transition-all cursor-pointer card-hover">
      <img src="https://picsum.photos/seed/{it['seed']}/600/400" alt="{it['title']} — {it['cat_label']} project" class="w-full h-52 object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy"/>
      <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-5" aria-hidden="true">
        <div><span class="text-xs font-semibold text-primary bg-white/20 px-2 py-0.5 rounded-full">{it['cat_label']}</span><h3 class="text-white font-black text-lg mt-1">{it['title']}</h3></div>
      </div>
      <div class="p-4 bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800">
        <span class="text-xs font-semibold text-primary uppercase tracking-wider">{it['cat_label']}</span>
        <h3 class="font-bold mt-0.5 dark:text-white">{it['title']}</h3>
      </div>
    </article>\n    """

    x_data = 'x-data="{filter:\'all\'}"' if pf else ""
    body = f"""
{_section_page_hero(cfg, '<span class="gradient-text">Portfolio</span>',
    "A selection of our best work across design, development, and strategy.")}
<section class="py-24 px-4" {x_data}>
  <div class="max-w-6xl mx-auto">
    {"<div class='flex flex-wrap gap-3 justify-center mb-14 " + rv + "' role='group' aria-label='Filter projects'>" + filter_btns + "</div>" if pf else ""}
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">{cards}</div>
  </div>
</section>"""
    return _page_head(cfg, "Portfolio") + _navbar(cfg, "portfolio") + body + _footer(cfg)


def generate_blog(cfg: dict) -> str:
    if not cfg["features"]["blog"]:
        return ""
    anim  = cfg["features"]["animations"]
    rv    = "reveal" if anim else ""
    posts = cfg["content"].get("blog_posts", [])

    cards = ""
    for p in posts:
        cards += f"""<article class="{rv} card-hover bg-white dark:bg-gray-900 rounded-2xl overflow-hidden border border-gray-100 dark:border-gray-800">
      <img src="https://picsum.photos/seed/{p['seed']}/600/300" alt="{p['title']}" class="w-full h-44 object-cover" loading="lazy"/>
      <div class="p-5">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-semibold text-primary bg-primary-10 px-2.5 py-0.5 rounded-full">{p['tag']}</span>
          <time class="text-xs text-gray-400" datetime="{p['datetime']}">{p['date']}</time>
        </div>
        <h2 class="font-black text-base mb-2 leading-snug dark:text-white">{p['title']}</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed mb-4">{p['excerpt']}</p>
        <div class="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-800">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-full btn-gradient flex items-center justify-center text-white text-xs font-bold" aria-hidden="true">{p['initials']}</div>
            <span class="text-xs text-gray-500">{p['author']}</span>
          </div>
          <a href="#" class="text-xs font-semibold text-primary hover:underline focus:outline-none focus:ring-2 focus:ring-[var(--primary)] rounded" aria-label="Read {p['title']}">Read →</a>
        </div>
      </div>
    </article>\n    """

    body = f"""
{_section_page_hero(cfg, 'Our <span class="gradient-text">Blog</span>',
    "Thoughts, insights, and expertise from our team.")}
<section class="py-24 px-4">
  <div class="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{cards}</div>
</section>"""
    return _page_head(cfg, "Blog") + _navbar(cfg, "blog") + body + _footer(cfg)


def generate_contact(cfg: dict) -> str:
    anim = cfg["features"]["animations"]
    rv   = "reveal" if anim else ""
    rvl  = "reveal-left" if anim else ""
    rvr  = "reveal-right" if anim else ""
    name = cfg["site_name"]

    body = f"""
{_section_page_hero(cfg, 'Contact <span class="gradient-text">Us</span>',
    "Have a question or project in mind? We'd love to hear from you.")}
<section class="py-24 px-4">
  <div class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-14">
    <div class="{rvl} space-y-5">
      <div>
        <h2 class="text-2xl font-black mb-2 dark:text-white">Let's <span class="gradient-text">Talk</span></h2>
        <p class="text-gray-500 dark:text-gray-400 leading-relaxed">Whether you're a startup looking to scale or an enterprise exploring new solutions, our team is ready to help.</p>
      </div>
      <div class="space-y-3">
        <div class="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 card-hover"><span class="text-2xl" aria-hidden="true">📧</span><div><div class="font-semibold text-sm dark:text-white">Email</div><div class="text-sm text-gray-500">hello@{name.lower().replace(' ','')}.io</div></div></div>
        <div class="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 card-hover"><span class="text-2xl" aria-hidden="true">📞</span><div><div class="font-semibold text-sm dark:text-white">Phone</div><div class="text-sm text-gray-500">+1 (555) 000-1234</div></div></div>
        <div class="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 card-hover"><span class="text-2xl" aria-hidden="true">📍</span><div><div class="font-semibold text-sm dark:text-white">Address</div><div class="text-sm text-gray-500">123 Tech Street, San Francisco, CA</div></div></div>
        <div class="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 card-hover"><span class="text-2xl" aria-hidden="true">🕐</span><div><div class="font-semibold text-sm dark:text-white">Hours</div><div class="text-sm text-gray-500">Mon–Fri, 9am–6pm PST</div></div></div>
      </div>
    </div>
    <div class="{rvr}">
      <form id="contactForm" class="glass rounded-2xl p-8 border border-gray-100 dark:border-gray-700 space-y-5" novalidate aria-label="Contact form">
        <h2 class="text-xl font-black dark:text-white">Send a Message</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div><label for="firstName" class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">First Name</label><input id="firstName" type="text" name="firstName" required placeholder="John" autocomplete="given-name" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:outline-none focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20 transition-all dark:text-white"/></div>
          <div><label for="lastName" class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Last Name</label><input id="lastName" type="text" name="lastName" required placeholder="Doe" autocomplete="family-name" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:outline-none focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20 transition-all dark:text-white"/></div>
        </div>
        <div><label for="email" class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Email</label><input id="email" type="email" name="email" required placeholder="john@company.com" autocomplete="email" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:outline-none focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20 transition-all dark:text-white"/></div>
        <div><label for="message" class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Message</label><textarea id="message" name="message" required rows="5" placeholder="Tell us how we can help…" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:outline-none focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20 transition-all resize-none dark:text-white"></textarea></div>
        <button type="submit" class="w-full btn-gradient py-3 rounded-full font-bold text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:ring-offset-2" aria-label="Send message">Send Message ✉️</button>
        <p class="text-xs text-gray-400 text-center">We'll respond within 24 hours.</p>
      </form>
    </div>
  </div>
</section>"""
    return _page_head(cfg, "Contact") + _navbar(cfg, "contact") + body + _footer(cfg)


def generate_pricing(cfg: dict) -> str:
    anim   = cfg["features"]["animations"]
    rv     = "reveal" if anim else ""
    toggle = cfg["features"]["pricing_toggle"]
    tiers  = cfg["content"].get("pricing", [])

    x_data = 'x-data="{yearly:false}"' if toggle else ""
    toggle_html = """<div class="inline-flex items-center gap-1 bg-gray-100 dark:bg-gray-800 rounded-full p-1 mt-6" role="group" aria-label="Billing period">
      <button @click="yearly=false" :class="!yearly?'btn-gradient':'text-gray-500 dark:text-gray-400'" class="px-5 py-2 rounded-full text-sm font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-[var(--primary)]" :aria-pressed="(!yearly).toString()">Monthly</button>
      <button @click="yearly=true"  :class="yearly?'btn-gradient':'text-gray-500 dark:text-gray-400'" class="px-5 py-2 rounded-full text-sm font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-[var(--primary)]" :aria-pressed="yearly.toString()">Yearly <span class="text-xs font-bold text-emerald-500 ml-1">-20%</span></button>
    </div>""" if toggle else ""

    cards = ""
    for t in tiers:
        featured_cls = "border-2 border-[var(--primary)] shadow-glow" if t.get("featured") else "border border-gray-200 dark:border-gray-700"
        badge = '<div class="absolute -top-3.5 left-1/2 -translate-x-1/2 btn-gradient px-4 py-1 rounded-full text-xs font-black whitespace-nowrap">Most Popular</div>' if t.get("featured") else ""
        pm = t["price_monthly"]
        py = t["price_yearly"]
        price_html = f'<span x-text="yearly ? \'${py}\' : \'${pm}\'"></span><span class="text-lg font-normal text-gray-400">/mo</span>' if toggle and isinstance(pm, int) else f'<span>{pm if isinstance(pm,str) else "$"+str(pm)}</span>{"<span class=\"text-lg font-normal text-gray-400\">/mo</span>" if isinstance(pm,int) else ""}'
        feats = "".join(f'<li class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300"><span class="text-primary font-bold" aria-hidden="true">✓</span>{f}</li>' for f in t.get("features",[]))
        missing = "".join(f'<li class="flex items-center gap-2 text-sm text-gray-400 line-through" aria-label="Not included: {f}">{f}</li>' for f in t.get("missing",[]))
        btn_cls = "btn-gradient" if t.get("featured") else "btn-outline-primary"
        cards += f"""<div class="{rv} card-hover relative bg-white dark:bg-gray-900 {featured_cls} rounded-2xl p-8 flex flex-col text-left">
      {badge}
      <div class="text-sm font-semibold {'text-primary' if t.get('featured') else 'text-gray-500 dark:text-gray-400'} uppercase tracking-wider mb-3">{t['tier']}</div>
      <div class="text-5xl font-black dark:text-white mb-1">{price_html}</div>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-6">{t['desc']}</p>
      <ul class="space-y-3 mb-8 flex-1" role="list">{feats}{missing}</ul>
      <a href="contact.html" class="{btn_cls} py-3 rounded-full font-bold text-sm text-center block focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:ring-offset-2">{'Start Free Trial' if t.get('featured') else 'Get Started'}</a>
    </div>\n    """

    body = f"""
{_section_page_hero(cfg, '<span class="gradient-text">Transparent</span> Pricing',
    "No hidden fees. Scale up or down at any time. Cancel whenever you want.")}
<section class="py-24 px-4" {x_data}>
  <div class="max-w-3xl mx-auto text-center mb-4 {rv}">{toggle_html}</div>
  <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-{len(tiers)} gap-6 items-start">{cards}</div>
</section>"""
    return _page_head(cfg, "Pricing") + _navbar(cfg, "pricing") + body + _footer(cfg)


def generate_team(cfg: dict) -> str:
    anim = cfg["features"]["animations"]
    rv   = "reveal" if anim else ""
    team = cfg["content"].get("team", [])

    cards = ""
    for m in team:
        cards += f"""<article class="{rv} card-hover card-gradient-border group bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl p-7 text-center">
      <div class="w-20 h-20 rounded-full btn-gradient flex items-center justify-center text-white font-black text-2xl mx-auto mb-4 group-hover:scale-110 transition-transform" aria-hidden="true">{m['initials']}</div>
      <h2 class="font-black text-base dark:text-white">{m['name']}</h2>
      <div class="text-xs text-primary font-semibold mt-0.5 mb-3">{m['role']}</div>
      <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">{m['bio']}</p>
    </article>\n    """

    body = f"""
{_section_page_hero(cfg, 'Meet the <span class="gradient-text">Team</span>',
    f"The passionate people behind {cfg['site_name']} — engineers, designers, and builders.")}
<section class="py-24 px-4">
  <div class="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">{cards}</div>
</section>"""
    return _page_head(cfg, "Team") + _navbar(cfg, "team") + body + _footer(cfg)


def generate_faq(cfg: dict) -> str:
    anim = cfg["features"]["animations"]
    rv   = "reveal" if anim else ""
    faqs = cfg["content"].get("faq", [])

    items = ""
    for i, faq in enumerate(faqs):
        items += f"""<div x-data="{{open:false}}" class="{rv} glass rounded-2xl border border-gray-100 dark:border-gray-800 overflow-hidden">
      <button @click="open=!open" :aria-expanded="open.toString()" aria-controls="faq{i}"
              class="w-full flex items-center justify-between px-6 py-5 text-left focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:ring-inset">
        <span class="font-semibold text-sm dark:text-white">{faq['q']}</span>
        <span :class="open?'rotate-45':''" class="text-primary text-xl font-bold transition-transform duration-200 flex-shrink-0 ml-4" aria-hidden="true">+</span>
      </button>
      <div id="faq{i}" x-show="open" x-transition class="px-6 pb-5">
        <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{faq['a']}</p>
      </div>
    </div>\n    """

    body = f"""
{_section_page_hero(cfg, 'Frequently Asked <span class="gradient-text">Questions</span>',
    "Quick answers to the questions we hear most often.")}
<section class="py-24 px-4">
  <div class="max-w-3xl mx-auto space-y-3">{items}</div>
</section>
<section class="py-16 px-4 bg-gray-50 dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800 text-center">
  <div class="max-w-xl mx-auto {rv}">
    <h2 class="text-2xl font-black mb-3 dark:text-white">Still have questions?</h2>
    <p class="text-gray-500 dark:text-gray-400 mb-6">Our team is happy to help. Reach out anytime.</p>
    <a href="contact.html" class="btn-gradient px-7 py-3 rounded-full font-bold text-sm inline-block focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:ring-offset-2">Contact Support</a>
  </div>
</section>"""
    return _page_head(cfg, "FAQ") + _navbar(cfg, "faq") + body + _footer(cfg)


def generate_testimonials(cfg: dict) -> str:
    anim = cfg["features"]["animations"]
    rv   = "reveal" if anim else ""
    tms  = cfg["content"].get("testimonials", [])

    cards = ""
    for t in tms:
        cards += f"""<blockquote class="{rv} card-hover card-gradient-border relative glass rounded-2xl p-7 border border-gray-100 dark:border-gray-800">
      <div class="absolute top-5 right-6 text-5xl text-primary opacity-20 font-black leading-none" aria-hidden="true">"</div>
      <div class="flex gap-0.5 mb-4 text-amber-400" aria-label="5 stars">⭐⭐⭐⭐⭐</div>
      <p class="text-sm text-gray-600 dark:text-gray-300 leading-relaxed italic mb-5">"{t['quote']}"</p>
      <footer class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full btn-gradient flex items-center justify-center text-white font-bold text-sm flex-shrink-0" aria-hidden="true">{t['initials']}</div>
        <div><cite class="font-semibold text-sm dark:text-white not-italic">{t['name']}</cite><div class="text-xs text-gray-400">{t['role']}</div></div>
      </footer>
    </blockquote>\n    """

    body = f"""
{_section_page_hero(cfg, f'What Our <span class="gradient-text">Customers Say</span>',
    f"Don't take our word for it — hear from the teams building with {cfg['site_name']} every day.")}
<section class="py-12 px-4 bg-gray-50 dark:bg-gray-900 border-b border-gray-100 dark:border-gray-800">
  <div class="max-w-4xl mx-auto flex flex-wrap items-center justify-center gap-8 {rv}">
    <div class="text-center"><div class="text-6xl font-black gradient-text" aria-label="4.9 out of 5 stars">4.9</div><div class="text-amber-400 text-xl mt-1" aria-hidden="true">⭐⭐⭐⭐⭐</div><div class="text-sm text-gray-500 dark:text-gray-400 mt-1">Average Rating</div></div>
    <div class="w-px h-16 bg-gray-200 dark:bg-gray-700 hidden sm:block" aria-hidden="true"></div>
    <div class="text-center"><div class="text-4xl font-black text-primary">2,400+</div><div class="text-sm text-gray-500 dark:text-gray-400 mt-1">Reviews</div></div>
    <div class="w-px h-16 bg-gray-200 dark:bg-gray-700 hidden sm:block" aria-hidden="true"></div>
    <div class="text-center"><div class="text-4xl font-black text-primary">98%</div><div class="text-sm text-gray-500 dark:text-gray-400 mt-1">Would Recommend</div></div>
  </div>
</section>
<section class="py-24 px-4">
  <div class="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-{min(len(tms),3)} gap-6">{cards}</div>
</section>"""
    return _page_head(cfg, "Testimonials") + _navbar(cfg, "testimonials") + body + _footer(cfg)


# ── Page dispatch map ─────────────────────────────────────────────────────────
PAGE_GENERATORS = {
    "home":         ("index.html",        generate_home),
    "about":        ("about.html",        generate_about),
    "services":     ("services.html",     generate_services),
    "portfolio":    ("portfolio.html",    generate_portfolio),
    "blog":         ("blog.html",         generate_blog),
    "contact":      ("contact.html",      generate_contact),
    "pricing":      ("pricing.html",      generate_pricing),
    "team":         ("team.html",         generate_team),
    "faq":          ("faq.html",          generate_faq),
    "testimonials": ("testimonials.html", generate_testimonials),
}
