/**
 * blocks.js — Block-Based Component Library
 * Each block: { type, label, icon, category, defaultProps, defaultStyles, render() }
 * render() returns clean HTML string for preview injection.
 */
'use strict';

// ── Block registry ────────────────────────────────────────────────────────────

const BLOCK_CATEGORIES = ['Hero', 'Features', 'Pricing', 'Testimonials', 'CTA', 'Content', 'Media', 'Contact'];

const BLOCKS = [

  // ── HERO ──────────────────────────────────────────────────────────────────

  {
    type: 'hero_centered', label: 'Hero — Centered', icon: '🎯', category: 'Hero',
    defaultProps: {
      title: 'Build Something Amazing',
      subtitle: 'The fastest way to launch your next big idea.',
      cta_text: 'Get Started Free', cta_link: '#',
      cta2_text: 'See Demo', cta2_link: '#',
      badge: '🚀 Now in Beta'
    },
    defaultStyles: { bg: 'gradient', align: 'center', padding: 'xl', text_color: '#fff' },
    render(p, s, theme) {
      return `<section data-block="hero_centered" style="background:${s.bg==='gradient'?`linear-gradient(135deg,${theme.primary},${theme.secondary})`:(s.bg||theme.primary)};padding:${PAD[s.padding||'xl']};text-align:${s.align||'center'};color:${s.text_color||'#fff'}">
  ${p.badge?`<span style="display:inline-block;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.3);color:#fff;font-size:.75rem;font-weight:700;padding:.3rem .9rem;border-radius:999px;margin-bottom:1.5rem;letter-spacing:.05em">${esc(p.badge)}</span>`:''}
  <h1 style="font-size:clamp(2rem,5vw,3.5rem);font-weight:800;line-height:1.1;margin:0 0 1rem;max-width:800px;margin-inline:auto">${esc(p.title)}</h1>
  <p style="font-size:1.2rem;opacity:.85;max-width:560px;margin:0 auto 2.5rem;line-height:1.6">${esc(p.subtitle)}</p>
  <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">
    <a href="${esc(p.cta_link)}" style="background:#fff;color:${theme.primary};padding:.85rem 2rem;border-radius:.75rem;font-weight:700;text-decoration:none;font-size:1rem;transition:transform .15s" onmouseover="this.style.transform='scale(1.04)'" onmouseout="this.style.transform=''">${esc(p.cta_text)}</a>
    ${p.cta2_text?`<a href="${esc(p.cta2_link)}" style="background:rgba(255,255,255,.15);color:#fff;padding:.85rem 2rem;border-radius:.75rem;font-weight:700;text-decoration:none;font-size:1rem;border:1px solid rgba(255,255,255,.3)">${esc(p.cta2_text)}</a>`:''}
  </div>
</section>`;
    }
  },

  {
    type: 'hero_split', label: 'Hero — Split', icon: '⬛', category: 'Hero',
    defaultProps: {
      title: 'Ship Faster Than Ever', subtitle: 'Automate your workflow and focus on what matters.',
      cta_text: 'Start Free Trial', cta_link: '#',
      image: 'https://images.unsplash.com/photo-1551434678-e076c223a692?w=600&q=80'
    },
    defaultStyles: { bg: '#0f0f1a', align: 'left', padding: 'xl', text_color: '#fff' },
    render(p, s, theme) {
      return `<section data-block="hero_split" style="background:${s.bg||'#0f0f1a'};padding:${PAD[s.padding||'xl']};color:${s.text_color||'#fff'}">
  <div style="max-width:1200px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center">
    <div>
      <h1 style="font-size:clamp(1.8rem,4vw,3rem);font-weight:800;line-height:1.15;margin:0 0 1.25rem">${esc(p.title)}</h1>
      <p style="font-size:1.1rem;opacity:.75;margin:0 0 2rem;line-height:1.7">${esc(p.subtitle)}</p>
      <a href="${esc(p.cta_link)}" style="background:${theme.primary};color:#fff;padding:.85rem 2rem;border-radius:.75rem;font-weight:700;text-decoration:none;display:inline-block">${esc(p.cta_text)}</a>
    </div>
    <div style="border-radius:1.5rem;overflow:hidden;box-shadow:0 32px 64px rgba(0,0,0,.4)">
      <img src="${esc(p.image)}" alt="Hero" style="width:100%;height:auto;display:block"/>
    </div>
  </div>
</section>`;
    }
  },

  {
    type: 'hero_minimal', label: 'Hero — Minimal', icon: '✦', category: 'Hero',
    defaultProps: { title: 'Simple. Fast. Powerful.', subtitle: 'Everything you need, nothing you don\'t.', cta_text: 'Get Started', cta_link: '#' },
    defaultStyles: { bg: '#fff', align: 'center', padding: 'xl', text_color: '#111' },
    render(p, s, theme) {
      return `<section data-block="hero_minimal" style="background:${s.bg||'#fff'};padding:${PAD[s.padding||'xl']};text-align:center;color:${s.text_color||'#111'}">
  <h1 style="font-size:clamp(2rem,5vw,4rem);font-weight:900;letter-spacing:-.03em;margin:0 0 1rem;background:linear-gradient(135deg,${theme.primary},${theme.secondary});-webkit-background-clip:text;-webkit-text-fill-color:transparent">${esc(p.title)}</h1>
  <p style="font-size:1.15rem;color:#666;max-width:500px;margin:0 auto 2rem;line-height:1.6">${esc(p.subtitle)}</p>
  <a href="${esc(p.cta_link)}" style="background:${theme.primary};color:#fff;padding:.85rem 2.5rem;border-radius:999px;font-weight:700;text-decoration:none;font-size:1rem">${esc(p.cta_text)}</a>
</section>`;
    }
  },

  // ── FEATURES ──────────────────────────────────────────────────────────────

  {
    type: 'features_grid', label: 'Features — Grid', icon: '⚡', category: 'Features',
    defaultProps: {
      title: 'Everything You Need',
      subtitle: 'Built for teams that move fast.',
      items: [
        { icon: '⚡', title: 'Lightning Fast', desc: 'Sub-100ms response times globally.' },
        { icon: '🔒', title: 'Secure by Default', desc: 'SOC 2 certified infrastructure.' },
        { icon: '📈', title: 'Auto Scaling', desc: 'Handle any traffic spike effortlessly.' },
        { icon: '🤖', title: 'AI Powered', desc: 'Smart insights built right in.' },
        { icon: '🔗', title: '200+ Integrations', desc: 'Connect your favorite tools.' },
        { icon: '🌍', title: 'Global CDN', desc: 'Deploy to 50+ edge locations.' }
      ]
    },
    defaultStyles: { bg: '#f8f9ff', padding: 'xl', cols: 3 },
    render(p, s, theme) {
      const items = (p.items||[]).map(i => `
    <div style="background:#fff;border-radius:1rem;padding:1.75rem;box-shadow:0 2px 16px rgba(0,0,0,.06);border:1px solid #f0f0f0">
      <div style="font-size:2rem;margin-bottom:.75rem">${i.icon||'⚡'}</div>
      <h3 style="font-size:1.05rem;font-weight:700;color:#111;margin:0 0 .5rem">${esc(i.title)}</h3>
      <p style="font-size:.9rem;color:#666;margin:0;line-height:1.6">${esc(i.desc)}</p>
    </div>`).join('');
      return `<section data-block="features_grid" style="background:${s.bg||'#f8f9ff'};padding:${PAD[s.padding||'xl']}">
  <div style="max-width:1200px;margin:0 auto">
    <div style="text-align:center;margin-bottom:3rem">
      <h2 style="font-size:clamp(1.5rem,3vw,2.5rem);font-weight:800;color:#111;margin:0 0 .75rem">${esc(p.title)}</h2>
      <p style="font-size:1.05rem;color:#666;max-width:500px;margin:0 auto">${esc(p.subtitle)}</p>
    </div>
    <div style="display:grid;grid-template-columns:repeat(${s.cols||3},1fr);gap:1.5rem">${items}</div>
  </div>
</section>`;
    }
  },

  // ── PRICING ───────────────────────────────────────────────────────────────

  {
    type: 'pricing_cards', label: 'Pricing — Cards', icon: '💰', category: 'Pricing',
    defaultProps: {
      title: 'Simple, Transparent Pricing',
      subtitle: 'No hidden fees. Cancel anytime.',
      tiers: [
        { name: 'Starter', price: '$0', period: '/mo', desc: 'For side projects', features: ['3 projects', '100GB bandwidth', 'Community support'], cta: 'Get Started', featured: false },
        { name: 'Pro', price: '$49', period: '/mo', desc: 'For growing teams', features: ['Unlimited projects', '1TB bandwidth', 'Priority support', 'Custom domains'], cta: 'Start Free Trial', featured: true },
        { name: 'Enterprise', price: 'Custom', period: '', desc: 'For large orgs', features: ['Everything in Pro', 'Dedicated support', 'SSO / SAML', 'SLA guarantee'], cta: 'Contact Sales', featured: false }
      ]
    },
    defaultStyles: { bg: '#fff', padding: 'xl' },
    render(p, s, theme) {
      const cards = (p.tiers||[]).map(t => `
    <div style="border-radius:1.25rem;padding:2rem;border:${t.featured?`2px solid ${theme.primary}`:'1px solid #e5e7eb'};background:${t.featured?`linear-gradient(135deg,${theme.primary},${theme.secondary})`:'#fff'};color:${t.featured?'#fff':'#111'};position:relative">
      ${t.featured?`<div style="position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:#fff;color:${theme.primary};font-size:.7rem;font-weight:800;padding:.25rem .75rem;border-radius:999px;border:2px solid ${theme.primary}">MOST POPULAR</div>`:''}
      <div style="font-size:.85rem;font-weight:700;opacity:.7;margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.05em">${esc(t.name)}</div>
      <div style="font-size:2.5rem;font-weight:900;margin-bottom:.25rem">${esc(t.price)}<span style="font-size:1rem;font-weight:400;opacity:.7">${esc(t.period)}</span></div>
      <div style="font-size:.9rem;opacity:.7;margin-bottom:1.5rem">${esc(t.desc)}</div>
      <ul style="list-style:none;padding:0;margin:0 0 1.5rem;space-y:0">
        ${(t.features||[]).map(f=>`<li style="padding:.4rem 0;font-size:.9rem;display:flex;align-items:center;gap:.5rem"><span style="color:${t.featured?'rgba(255,255,255,.8)':'#10b981'}">✓</span>${esc(f)}</li>`).join('')}
      </ul>
      <a href="#" style="display:block;text-align:center;padding:.85rem;border-radius:.75rem;font-weight:700;text-decoration:none;background:${t.featured?'rgba(255,255,255,.2)':theme.primary};color:${t.featured?'#fff':'#fff'};border:${t.featured?'1px solid rgba(255,255,255,.3)':'none'}">${esc(t.cta)}</a>
    </div>`).join('');
      return `<section data-block="pricing_cards" style="background:${s.bg||'#fff'};padding:${PAD[s.padding||'xl']}">
  <div style="max-width:1100px;margin:0 auto">
    <div style="text-align:center;margin-bottom:3rem">
      <h2 style="font-size:clamp(1.5rem,3vw,2.5rem);font-weight:800;color:#111;margin:0 0 .75rem">${esc(p.title)}</h2>
      <p style="color:#666;font-size:1.05rem">${esc(p.subtitle)}</p>
    </div>
    <div style="display:grid;grid-template-columns:repeat(${p.tiers?.length||3},1fr);gap:1.5rem;align-items:start">${cards}</div>
  </div>
</section>`;
    }
  },

  // ── TESTIMONIALS ──────────────────────────────────────────────────────────

  {
    type: 'testimonials_grid', label: 'Testimonials — Grid', icon: '💬', category: 'Testimonials',
    defaultProps: {
      title: 'Loved by Thousands',
      items: [
        { name: 'Sarah Chen', role: 'CTO, TechFlow', quote: 'This cut our deployment time by 80%. Absolutely incredible.', initials: 'SC' },
        { name: 'Marcus Johnson', role: 'Lead Engineer', quote: "Best developer experience I've had in 10 years.", initials: 'MJ' },
        { name: 'Aisha Patel', role: 'VP Engineering', quote: 'We migrated 50+ microservices in a single weekend.', initials: 'AP' }
      ]
    },
    defaultStyles: { bg: '#f8f9ff', padding: 'xl' },
    render(p, s, theme) {
      const cards = (p.items||[]).map(i => `
    <div style="background:#fff;border-radius:1rem;padding:1.75rem;box-shadow:0 2px 16px rgba(0,0,0,.06)">
      <div style="font-size:1.5rem;color:${theme.primary};margin-bottom:1rem">❝</div>
      <p style="font-size:.95rem;color:#444;line-height:1.7;margin:0 0 1.25rem;font-style:italic">"${esc(i.quote)}"</p>
      <div style="display:flex;align-items:center;gap:.75rem">
        <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,${theme.primary},${theme.secondary});display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:.85rem;flex-shrink:0">${esc(i.initials)}</div>
        <div><div style="font-weight:700;font-size:.9rem;color:#111">${esc(i.name)}</div><div style="font-size:.8rem;color:#888">${esc(i.role)}</div></div>
      </div>
    </div>`).join('');
      return `<section data-block="testimonials_grid" style="background:${s.bg||'#f8f9ff'};padding:${PAD[s.padding||'xl']}">
  <div style="max-width:1100px;margin:0 auto">
    <h2 style="text-align:center;font-size:clamp(1.5rem,3vw,2.5rem);font-weight:800;color:#111;margin:0 0 3rem">${esc(p.title)}</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem">${cards}</div>
  </div>
</section>`;
    }
  },

  // ── CTA ───────────────────────────────────────────────────────────────────

  {
    type: 'cta_banner', label: 'CTA — Banner', icon: '📣', category: 'CTA',
    defaultProps: { title: 'Ready to Get Started?', subtitle: 'Join 10,000+ teams already using our platform.', cta_text: 'Start Free Trial', cta_link: '#', cta2_text: 'Talk to Sales', cta2_link: '#' },
    defaultStyles: { bg: 'gradient', padding: 'lg', text_color: '#fff' },
    render(p, s, theme) {
      return `<section data-block="cta_banner" style="background:${s.bg==='gradient'?`linear-gradient(135deg,${theme.primary},${theme.secondary})`:(s.bg||theme.primary)};padding:${PAD[s.padding||'lg']};text-align:center;color:${s.text_color||'#fff'}">
  <h2 style="font-size:clamp(1.5rem,3vw,2.5rem);font-weight:800;margin:0 0 .75rem">${esc(p.title)}</h2>
  <p style="font-size:1.05rem;opacity:.85;margin:0 0 2rem">${esc(p.subtitle)}</p>
  <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">
    <a href="${esc(p.cta_link)}" style="background:#fff;color:${theme.primary};padding:.85rem 2rem;border-radius:.75rem;font-weight:700;text-decoration:none">${esc(p.cta_text)}</a>
    ${p.cta2_text?`<a href="${esc(p.cta2_link)}" style="background:rgba(255,255,255,.15);color:#fff;padding:.85rem 2rem;border-radius:.75rem;font-weight:700;text-decoration:none;border:1px solid rgba(255,255,255,.3)">${esc(p.cta2_text)}</a>`:''}
  </div>
</section>`;
    }
  },

  // ── FAQ ───────────────────────────────────────────────────────────────────

  {
    type: 'faq_accordion', label: 'FAQ — Accordion', icon: '❓', category: 'Content',
    defaultProps: {
      title: 'Frequently Asked Questions',
      items: [
        { q: 'How do I get started?', a: 'Sign up for free and follow our quick-start guide. You\'ll be up and running in under 5 minutes.' },
        { q: 'Is there a free plan?', a: 'Yes! Our free plan includes 3 projects and 100GB bandwidth with no credit card required.' },
        { q: 'Can I cancel anytime?', a: 'Absolutely. No contracts, no lock-in. Cancel with one click from your dashboard.' }
      ]
    },
    defaultStyles: { bg: '#fff', padding: 'xl' },
    render(p, s, theme) {
      const items = (p.items||[]).map((i, idx) => `
    <details style="border:1px solid #e5e7eb;border-radius:.75rem;overflow:hidden;margin-bottom:.75rem">
      <summary style="padding:1.25rem 1.5rem;font-weight:600;cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;color:#111">
        ${esc(i.q)}<span style="color:${theme.primary};font-size:1.25rem;transition:transform .2s">+</span>
      </summary>
      <div style="padding:0 1.5rem 1.25rem;color:#555;line-height:1.7;font-size:.95rem">${esc(i.a)}</div>
    </details>`).join('');
      return `<section data-block="faq_accordion" style="background:${s.bg||'#fff'};padding:${PAD[s.padding||'xl']}">
  <div style="max-width:720px;margin:0 auto">
    <h2 style="text-align:center;font-size:clamp(1.5rem,3vw,2.25rem);font-weight:800;color:#111;margin:0 0 2.5rem">${esc(p.title)}</h2>
    ${items}
  </div>
</section>`;
    }
  },

  // ── STATS ─────────────────────────────────────────────────────────────────

  {
    type: 'stats_row', label: 'Stats — Row', icon: '📊', category: 'Content',
    defaultProps: {
      items: [
        { value: '10K+', label: 'Happy Customers' },
        { value: '500+', label: 'Projects Shipped' },
        { value: '99.9%', label: 'Uptime SLA' },
        { value: '24/7', label: 'Support' }
      ]
    },
    defaultStyles: { bg: '#fff', padding: 'lg' },
    render(p, s, theme) {
      const items = (p.items||[]).map(i => `
    <div style="text-align:center;padding:1rem">
      <div style="font-size:2.5rem;font-weight:900;color:${theme.primary};line-height:1">${esc(i.value)}</div>
      <div style="font-size:.9rem;color:#666;margin-top:.5rem;font-weight:500">${esc(i.label)}</div>
    </div>`).join('');
      return `<section data-block="stats_row" style="background:${s.bg||'#fff'};padding:${PAD[s.padding||'lg']};border-top:1px solid #f0f0f0;border-bottom:1px solid #f0f0f0">
  <div style="max-width:900px;margin:0 auto;display:grid;grid-template-columns:repeat(${p.items?.length||4},1fr);gap:1rem">${items}</div>
</section>`;
    }
  },

  // ── CONTACT ───────────────────────────────────────────────────────────────

  {
    type: 'contact_form', label: 'Contact — Form', icon: '✉️', category: 'Contact',
    defaultProps: { title: 'Get in Touch', subtitle: 'We\'d love to hear from you.', cta_text: 'Send Message' },
    defaultStyles: { bg: '#f8f9ff', padding: 'xl' },
    render(p, s, theme) {
      return `<section data-block="contact_form" style="background:${s.bg||'#f8f9ff'};padding:${PAD[s.padding||'xl']}">
  <div style="max-width:560px;margin:0 auto">
    <h2 style="text-align:center;font-size:2rem;font-weight:800;color:#111;margin:0 0 .5rem">${esc(p.title)}</h2>
    <p style="text-align:center;color:#666;margin:0 0 2rem">${esc(p.subtitle)}</p>
    <form style="background:#fff;border-radius:1.25rem;padding:2rem;box-shadow:0 4px 24px rgba(0,0,0,.08)">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem">
        <input placeholder="First name" style="padding:.75rem 1rem;border:1px solid #e5e7eb;border-radius:.5rem;font-size:.95rem;width:100%;box-sizing:border-box"/>
        <input placeholder="Last name" style="padding:.75rem 1rem;border:1px solid #e5e7eb;border-radius:.5rem;font-size:.95rem;width:100%;box-sizing:border-box"/>
      </div>
      <input placeholder="Email address" style="width:100%;padding:.75rem 1rem;border:1px solid #e5e7eb;border-radius:.5rem;font-size:.95rem;margin-bottom:1rem;box-sizing:border-box"/>
      <textarea placeholder="Your message" rows="4" style="width:100%;padding:.75rem 1rem;border:1px solid #e5e7eb;border-radius:.5rem;font-size:.95rem;resize:vertical;margin-bottom:1.25rem;box-sizing:border-box"></textarea>
      <button type="submit" style="width:100%;background:${theme.primary};color:#fff;padding:.9rem;border:none;border-radius:.75rem;font-weight:700;font-size:1rem;cursor:pointer">${esc(p.cta_text)}</button>
    </form>
  </div>
</section>`;
    }
  },

];

// ── Helpers ───────────────────────────────────────────────────────────────────

const PAD = { sm: '2rem 1.5rem', md: '3rem 2rem', lg: '4rem 2rem', xl: '6rem 2rem', '2xl': '8rem 2rem' };

function esc(s) {
  return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Get block definition by type
function getBlock(type) {
  return BLOCKS.find(b => b.type === type) || null;
}

// Render a block from a config block object { type, props, styles }
function renderBlock(blockCfg, theme = { primary: '#6c63ff', secondary: '#f50057' }) {
  const def = getBlock(blockCfg.type);
  if (!def) return `<section style="padding:2rem;background:#fee;color:#c00;text-align:center">Unknown block: ${esc(blockCfg.type)}</section>`;
  const props  = Object.assign({}, def.defaultProps,  blockCfg.props  || {});
  const styles = Object.assign({}, def.defaultStyles, blockCfg.styles || {});
  return def.render(props, styles, theme);
}

// Create a new block config object from a block type
function createBlock(type) {
  const def = getBlock(type);
  if (!def) return null;
  return {
    id:     'blk_' + Math.random().toString(36).slice(2, 9),
    type:   def.type,
    props:  JSON.parse(JSON.stringify(def.defaultProps)),
    styles: JSON.parse(JSON.stringify(def.defaultStyles)),
  };
}
