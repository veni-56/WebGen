/**
 * state.js — Centralized builder state + mutation helpers
 *
 * Exports:
 *   DEFAULT_CONFIG  — canonical default project config
 *   ALL_SECTIONS    — ordered list of valid section names
 *   TEMPLATES       — template presets
 *   validateConfig  — ensure a config object is structurally sound
 *   makeBlockId     — generate a unique block ID
 */
'use strict';

// ── Section catalogue ─────────────────────────────────────────────────────────
const ALL_SECTIONS = Object.freeze([
  'hero','stats','features','testimonials','cta',
  'about_story','services','portfolio','blog',
  'contact','pricing','team','faq',
]);

// ── Template presets ──────────────────────────────────────────────────────────
const TEMPLATES = Object.freeze([
  { name:'NovaTech',     emoji:'🚀', desc:'SaaS startup',      primary:'#6c63ff', secondary:'#f50057', site_name:'NovaTech',     tagline:'Build the Future Faster Than Ever' },
  { name:'GreenLeaf',    emoji:'🌿', desc:'Eco / nature',       primary:'#2e7d32', secondary:'#ffc107', site_name:'GreenLeaf',    tagline:'Grow Sustainably, Scale Naturally' },
  { name:'OceanWave',    emoji:'🌊', desc:'Tech / blue',        primary:'#0277bd', secondary:'#00bcd4', site_name:'OceanWave',    tagline:'Ride the Wave of Innovation' },
  { name:'SunsetStudio', emoji:'🎨', desc:'Creative agency',    primary:'#e65100', secondary:'#f50057', site_name:'SunsetStudio', tagline:'Where Creativity Meets Technology' },
  { name:'DarkForge',    emoji:'⚙️', desc:'Developer tool',     primary:'#bb86fc', secondary:'#03dac6', site_name:'DarkForge',    tagline:'Forge the Future in the Dark' },
  { name:'GoldRush',     emoji:'💰', desc:'Finance / premium',  primary:'#b8860b', secondary:'#8b0000', site_name:'GoldRush',     tagline:'Premium Solutions for Premium Results' },
]);

// ── Default config ────────────────────────────────────────────────────────────
const DEFAULT_CONFIG = Object.freeze({
  site_name:   'NovaTech',
  tagline:     'Build the Future Faster Than Ever',
  description: 'Cutting-edge software solutions that help businesses scale, innovate, and lead.',
  cta_text:    'Start Free Trial',
  cta_link:    'contact.html',
  primary_color:   '#6c63ff',
  secondary_color: '#f50057',
  font: 'Inter',

  pages: {
    home:         { title:'Home',         file:'index.html',        sections:['hero','stats','features','testimonials','cta'], blocks:[] },
    about:        { title:'About',        file:'about.html',        sections:['about_story','cta'],                            blocks:[] },
    services:     { title:'Services',     file:'services.html',     sections:['services','cta'],                               blocks:[] },
    portfolio:    { title:'Portfolio',    file:'portfolio.html',    sections:['portfolio'],                                    blocks:[] },
    blog:         { title:'Blog',         file:'blog.html',         sections:['blog'],                                         blocks:[] },
    contact:      { title:'Contact',      file:'contact.html',      sections:['contact'],                                      blocks:[] },
    pricing:      { title:'Pricing',      file:'pricing.html',      sections:['pricing'],                                      blocks:[] },
    team:         { title:'Team',         file:'team.html',         sections:['team'],                                         blocks:[] },
    faq:          { title:'FAQ',          file:'faq.html',          sections:['faq'],                                          blocks:[] },
    testimonials: { title:'Testimonials', file:'testimonials.html', sections:['testimonials'],                                 blocks:[] },
  },

  features: {
    dark_mode:         true,
    animations:        true,
    blog:              true,
    portfolio_filter:  true,
    pricing_toggle:    true,
    scroll_progress:   true,
    back_to_top:       true,
    newsletter:        true,
    counter_animation: true,
  },

  plugins: {
    google_analytics: { enabled:false, tracking_id:'G-XXXXXXXXXX' },
    whatsapp:         { enabled:false, phone:'919876543210', message:'Hello!' },
    newsletter_popup: { enabled:false, delay_seconds:5, title:'Get Updates', subtitle:'No spam.' },
  },

  content: {
    stats: [
      { value:10000, suffix:'+',   label:'Happy Clients' },
      { value:500,   suffix:'+',   label:'Projects Shipped' },
      { value:99,    suffix:'.9%', label:'Uptime SLA' },
      { value:24,    suffix:'/7',  label:'Support' },
    ],
    features: [
      { icon:'⚡', title:'Lightning Performance', desc:'Sub-100ms response times globally.' },
      { icon:'🔒', title:'Enterprise Security',   desc:'SOC 2 Type II certified.' },
      { icon:'📈', title:'Auto Scaling',          desc:'Handle traffic spikes effortlessly.' },
      { icon:'🤖', title:'AI-Powered Insights',   desc:'Real-time analytics with AI.' },
      { icon:'🔗', title:'200+ Integrations',     desc:'Connect with Slack, GitHub, Stripe.' },
      { icon:'🌍', title:'Global CDN',            desc:'Deploy to 50+ edge locations.' },
    ],
    testimonials: [
      { initials:'SC', name:'Sarah Chen',     role:'CTO, TechFlow Inc.',    quote:'NovaTech cut our deployment time by 80%.' },
      { initials:'MJ', name:'Marcus Johnson', role:'Lead Engineer, StartupX', quote:"The best developer experience I've had in 10 years." },
      { initials:'AP', name:'Aisha Patel',    role:'VP Engineering, ScaleUp', quote:'We migrated 50+ microservices in a weekend.' },
    ],
    services: [
      { icon:'☁️', title:'Cloud Infrastructure', desc:'Deploy on our globally distributed edge network.', features:['50+ global edge locations','99.99% uptime SLA','Auto-scaling'] },
      { icon:'🤖', title:'AI & Machine Learning', desc:'Integrate powerful AI capabilities.',              features:['Pre-built model library','Custom fine-tuning','Real-time inference API'] },
      { icon:'🔒', title:'Security & Compliance', desc:'Enterprise-grade security.',                       features:['End-to-end encryption','SOC 2 certified','GDPR & HIPAA ready'] },
    ],
    team: [
      { initials:'AK', name:'Alex Kim',        role:'CEO & Co-founder', bio:'Former Google SWE.' },
      { initials:'SR', name:'Sofia Rodriguez', role:'CTO & Co-founder', bio:'Ex-Stripe infrastructure lead.' },
      { initials:'JL', name:'James Liu',       role:'Head of Design',   bio:'Previously at Figma.' },
      { initials:'MP', name:'Maya Patel',      role:'VP Engineering',   bio:'10+ years at Amazon and Airbnb.' },
    ],
    faq: [
      { q:'How long does it take to get started?', a:'You can be up and running in under 5 minutes.' },
      { q:'Do you offer a free plan?',             a:'Yes! Our free plan includes 3 projects, 100GB bandwidth.' },
      { q:'Is my data secure?',                    a:'Yes. We are SOC 2 Type II certified.' },
    ],
    pricing: [
      { tier:'Starter',    price_monthly:0,        price_yearly:0,        desc:'Perfect for side projects.', featured:false, features:['3 projects','100 GB bandwidth','Community support'],                                    missing:['Custom domains','Team seats'] },
      { tier:'Pro',        price_monthly:49,        price_yearly:39,       desc:'For growing teams.',         featured:true,  features:['Unlimited projects','1 TB bandwidth','Email support','Custom domains','5 team seats'], missing:[] },
      { tier:'Enterprise', price_monthly:'Custom',  price_yearly:'Custom', desc:'For large teams.',           featured:false, features:['Everything in Pro','Unlimited bandwidth','Dedicated support','SSO / SAML'],            missing:[] },
    ],
    blog_posts: [
      { seed:'b1', tag:'Design',   date:'May 1, 2025',  datetime:'2025-05-01', title:'The Future of Web Design',    excerpt:'Exploring trends that will shape the web.', author:'Sarah Chen',  initials:'SC' },
      { seed:'b2', tag:'Tech',     date:'Apr 20, 2025', datetime:'2025-04-20', title:'Building Scalable APIs',      excerpt:'Best practices for designing APIs.',        author:'Mike Ross',   initials:'MR' },
      { seed:'b3', tag:'Business', date:'Apr 10, 2025', datetime:'2025-04-10', title:'Growth Hacking for Startups', excerpt:'Proven strategies to accelerate growth.',   author:'Priya Patel', initials:'PP' },
    ],
    portfolio_items: [
      { seed:'p1', title:'E-Commerce Platform', category:'web',    cat_label:'Web Design' },
      { seed:'p2', title:'Brand Identity',      category:'brand',  cat_label:'Branding' },
      { seed:'p3', title:'Mobile Banking App',  category:'mobile', cat_label:'Mobile' },
      { seed:'p4', title:'SaaS Dashboard',      category:'saas',   cat_label:'SaaS' },
    ],
  },
});

// ── Unique block ID ───────────────────────────────────────────────────────────
function makeBlockId() {
  return 'blk_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
}

// ── Config validation + repair ────────────────────────────────────────────────
/**
 * validateConfig(cfg) — delegates to schema.js if loaded, otherwise runs
 * the structural repair logic directly.
 * Always returns a safe, usable config object.
 */
function validateConfig(cfg) {
  // If schema.js is loaded, use the full schema validator (returns { config, errors })
  if (typeof BLOCK_CONTRACTS !== 'undefined' && typeof updateConfig === 'function') {
    // schema.js validateConfig is named the same — call it via the schema module's version
    // We detect it by checking for the schema-specific exports
    const result = _schemaValidateConfig(cfg);
    if (result && result.config) {
      if (result.errors?.length) {
        Logger.log('CONFIG_ERROR', { errors: result.errors });
      }
      return result.config;
    }
  }

  // Fallback structural repair (no schema.js)
  if (!cfg || typeof cfg !== 'object') return JSON.parse(JSON.stringify(DEFAULT_CONFIG));

  const out = JSON.parse(JSON.stringify(cfg));

  const scalars = ['site_name','tagline','description','cta_text','cta_link','primary_color','secondary_color','font'];
  for (const k of scalars) {
    if (!out[k]) out[k] = DEFAULT_CONFIG[k];
  }

  if (!out.pages || typeof out.pages !== 'object') {
    out.pages = JSON.parse(JSON.stringify(DEFAULT_CONFIG.pages));
  } else {
    for (const [key, page] of Object.entries(out.pages)) {
      if (!Array.isArray(page.sections)) page.sections = [];
      if (!Array.isArray(page.blocks))   page.blocks   = [];
      if (!page.title) page.title = key;
      if (!page.file)  page.file  = key + '.html';
    }
  }

  if (!out.features || typeof out.features !== 'object') {
    out.features = JSON.parse(JSON.stringify(DEFAULT_CONFIG.features));
  }

  if (!out.content || typeof out.content !== 'object') {
    out.content = JSON.parse(JSON.stringify(DEFAULT_CONFIG.content));
  } else {
    const arrays = ['stats','features','testimonials','services','team','faq','pricing','blog_posts','portfolio_items'];
    for (const k of arrays) {
      if (!Array.isArray(out.content[k])) out.content[k] = JSON.parse(JSON.stringify(DEFAULT_CONFIG.content[k] || []));
    }
  }

  for (const page of Object.values(out.pages)) {
    page.blocks = (page.blocks || []).map(b => ({
      ...b,
      id:     b.id     || makeBlockId(),
      props:  b.props  || {},
      styles: b.styles || {},
    }));
  }

  return out;
}

// Internal alias — schema.js exports its own validateConfig with the same name.
// When both files are loaded, the last definition wins in the global scope.
// state.js defines it first; schema.js overrides it with the full version.
// This alias lets state.js call the schema version if available.
function _schemaValidateConfig(cfg) {
  // This will be overridden by schema.js's validateConfig at runtime
  return null;
}
