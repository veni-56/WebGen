/**
 * plugins/analytics/index.js — Analytics plugin.
 * Supports: Google Analytics 4, Plausible, Fathom.
 * Hook: afterRender — injects tracking script into each page.
 */
'use strict';

const AnalyticsPlugin = {
  id:      'analytics',
  name:    'Analytics',
  version: '1.0.0',

  settings: {
    provider:    'none',   // 'ga4' | 'plausible' | 'fathom' | 'none'
    tracking_id: '',       // GA4: G-XXXXXXXX, Plausible: domain, Fathom: site ID
    anonymize_ip: true,
  },

  hooks: {
    afterRender(ctx) {
      if (!ctx.html) return;
      const s = ctx._pluginSettings?.analytics || {};
      const snippet = AnalyticsPlugin._buildSnippet(s);
      if (snippet) {
        ctx.html = ctx.html.replace('</head>', snippet + '\n</head>');
      }
    },
  },

  _buildSnippet(s) {
    switch (s.provider) {
      case 'ga4':
        if (!s.tracking_id) return '';
        return `<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=${s.tracking_id}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${s.tracking_id}'${s.anonymize_ip?",{'anonymize_ip':true}":''})</script>`;

      case 'plausible':
        if (!s.tracking_id) return '';
        return `<!-- Plausible Analytics -->
<script defer data-domain="${s.tracking_id}" src="https://plausible.io/js/script.js"></script>`;

      case 'fathom':
        if (!s.tracking_id) return '';
        return `<!-- Fathom Analytics -->
<script src="https://cdn.usefathom.com/script.js" data-site="${s.tracking_id}" defer></script>`;

      default:
        return '';
    }
  },

  render() { return null; },
  validate(cfg) { return []; },
  onEnable(s)   { console.info('[Analytics Plugin] enabled', s.provider); },
  onDisable()   { console.info('[Analytics Plugin] disabled'); },
};

if (typeof WBS_SDK !== 'undefined') {
  WBS_SDK.registerPlugin(AnalyticsPlugin);
}
