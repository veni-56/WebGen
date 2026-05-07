/**
 * plugins/seo/index.js — SEO plugin.
 *
 * Injects: <title>, <meta description>, Open Graph tags, canonical URL.
 * Hook: afterRender — appends tags to <head> of each page.
 */
'use strict';

const SEOPlugin = {
  id:      'seo',
  name:    'SEO',
  version: '1.0.0',

  settings: {
    title_suffix:    '',          // e.g. ' | My Company'
    default_desc:    '',
    og_image:        '',
    canonical_base:  '',          // e.g. 'https://mysite.com'
    robots:          'index, follow',
  },

  hooks: {
    afterRender(ctx) {
      // ctx.html is the page HTML; ctx.cfg is the project config
      if (!ctx.html || !ctx.cfg) return;
      const s   = ctx._pluginSettings?.seo || {};
      const cfg = ctx.cfg;

      const title = (cfg.site_name || '') + (s.title_suffix || '');
      const desc  = cfg.description || s.default_desc || '';
      const image = s.og_image || '';
      const canon = s.canonical_base ? `${s.canonical_base}/${ctx.pageKey || ''}` : '';

      const tags = [
        title  ? `<title>${_esc(title)}</title>` : '',
        desc   ? `<meta name="description" content="${_esc(desc)}">` : '',
        `<meta name="robots" content="${_esc(s.robots || 'index, follow')}">`,
        title  ? `<meta property="og:title" content="${_esc(title)}">` : '',
        desc   ? `<meta property="og:description" content="${_esc(desc)}">` : '',
        image  ? `<meta property="og:image" content="${_esc(image)}">` : '',
        canon  ? `<link rel="canonical" href="${_esc(canon)}">` : '',
        `<meta property="og:type" content="website">`,
      ].filter(Boolean).join('\n  ');

      // Inject into <head> (replace existing title if present)
      ctx.html = ctx.html
        .replace(/<title>[^<]*<\/title>/i, '')
        .replace('</head>', `  ${tags}\n</head>`);
    },
  },

  render() { return null; },   // no visible block output

  validate(cfg) {
    const errors = [];
    if (!cfg.site_name) errors.push('SEO: site_name is empty');
    if (!cfg.description) errors.push('SEO: description is empty (affects search ranking)');
    return errors;
  },

  onEnable(settings) {
    console.info('[SEO Plugin] enabled', settings);
  },

  onDisable() {
    console.info('[SEO Plugin] disabled');
  },
};

function _esc(s) {
  return String(s || '').replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// Auto-register if SDK is available
if (typeof WBS_SDK !== 'undefined') {
  WBS_SDK.registerPlugin(SEOPlugin);
}
