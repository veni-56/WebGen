/**
 * marketplace/template.js — Template package format, import, export, validation.
 */
'use strict';

const TemplateMarketplace = (() => {
  const REQUIRED = ['id', 'name', 'version', 'pages'];

  function validate(tpl) {
    const errors = [];
    for (const f of REQUIRED) {
      if (!tpl[f]) errors.push(`Missing: "${f}"`);
    }
    if (tpl.theme?.primary && !/^#[0-9a-fA-F]{3,8}$/.test(tpl.theme.primary)) {
      errors.push('theme.primary must be a hex color');
    }
    return { valid: errors.length === 0, errors };
  }

  function importTemplate(tpl, currentCfg = {}) {
    const { valid, errors } = validate(tpl);
    if (!valid) throw new Error('Invalid template: ' + errors.join('; '));
    const cfg = JSON.parse(JSON.stringify(currentCfg));
    if (tpl.theme) {
      if (tpl.theme.primary)   cfg.primary_color   = tpl.theme.primary;
      if (tpl.theme.secondary) cfg.secondary_color = tpl.theme.secondary;
      if (tpl.theme.font)      cfg.font            = tpl.theme.font;
    }
    cfg.pages = { ...cfg.pages };
    for (const [key, page] of Object.entries(tpl.pages)) {
      cfg.pages[key] = {
        title:    page.title    || key,
        file:     page.file     || key + '.html',
        sections: page.sections || [],
        blocks:   (page.blocks  || []).map(b => ({
          ...b,
          id: 'blk_' + Math.random().toString(36).slice(2, 10),
        })),
      };
    }
    if (tpl.content) cfg.content = { ...cfg.content, ...tpl.content };
    if (tpl.plugins) cfg.plugins = { ...cfg.plugins, ...tpl.plugins };
    return cfg;
  }

  function exportTemplate(cfg, meta = {}) {
    return {
      id:          meta.id          || 'tpl_' + Date.now().toString(36),
      name:        meta.name        || cfg.site_name || 'My Template',
      description: meta.description || cfg.description || '',
      version:     meta.version     || '1.0.0',
      author:      meta.author      || '',
      preview:     meta.preview     || '',
      tags:        meta.tags        || [],
      theme: {
        primary:   cfg.primary_color   || '#6c63ff',
        secondary: cfg.secondary_color || '#f50057',
        font:      cfg.font            || 'Inter',
      },
      pages:   cfg.pages   || {},
      content: cfg.content || {},
      plugins: cfg.plugins || {},
    };
  }

  function downloadTemplate(cfg, meta = {}) {
    const tpl  = exportTemplate(cfg, meta);
    const blob = new Blob([JSON.stringify(tpl, null, 2)], { type: 'application/json' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = (tpl.name || 'template').toLowerCase().replace(/\s+/g, '_') + '.template.json';
    a.click();
    URL.revokeObjectURL(url);
  }

  async function loadFromFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = e => {
        try {
          const tpl = JSON.parse(e.target.result);
          const { valid, errors } = validate(tpl);
          if (!valid) reject(new Error(errors.join('; ')));
          else resolve(tpl);
        } catch(err) { reject(err); }
      };
      reader.onerror = () => reject(new Error('File read failed'));
      reader.readAsText(file);
    });
  }

  return { validate, importTemplate, exportTemplate, downloadTemplate, loadFromFile };
})();
