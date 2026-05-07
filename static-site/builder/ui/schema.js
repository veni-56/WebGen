/**
 * schema.js — Config schema, block contracts, and safe path-based updates.
 *
 * Exports:
 *   CONFIG_SCHEMA      — schema definition for the full config object
 *   BLOCK_CONTRACTS    — per-block-type prop/style contracts with defaults
 *   validateConfig     — validate + auto-fix a config against CONFIG_SCHEMA
 *   validateBlock      — validate a single block against its contract
 *   sanitizeBlock      — return a clean block with all required fields filled
 *   updateConfig       — safe path-based setter (e.g. "pages.home.title")
 *   updateBlockProp    — safe block prop setter with contract enforcement
 *   updateBlockStyle   — safe block style setter with contract enforcement
 */
'use strict';

// ─────────────────────────────────────────────────────────────────────────────
// 1. CONFIG SCHEMA
//    Each field: { type, required, default, enum?, min?, max?, items? }
// ─────────────────────────────────────────────────────────────────────────────

const CONFIG_SCHEMA = Object.freeze({
  // Top-level scalars
  site_name:       { type:'string',  required:true,  default:'My Site' },
  tagline:         { type:'string',  required:true,  default:'Welcome' },
  description:     { type:'string',  required:false, default:'' },
  cta_text:        { type:'string',  required:false, default:'Get Started' },
  cta_link:        { type:'string',  required:false, default:'#' },
  primary_color:   { type:'color',   required:true,  default:'#6c63ff' },
  secondary_color: { type:'color',   required:true,  default:'#f50057' },
  font:            { type:'string',  required:false, default:'Inter',
                     enum:['Inter','Poppins','Roboto','Nunito','Lato','Montserrat','Raleway','Open Sans'] },

  // Nested objects — validated structurally
  pages:    { type:'object', required:true  },
  features: { type:'object', required:false },
  plugins:  { type:'object', required:false },
  content:  { type:'object', required:true  },
});

// Schema for a single page entry
const PAGE_SCHEMA = Object.freeze({
  title:    { type:'string', required:true,  default:'Page' },
  file:     { type:'string', required:true,  default:'page.html' },
  slug:     { type:'string', required:false, default:'' },
  sections: { type:'array',  required:true,  default:[] },
  blocks:   { type:'array',  required:true,  default:[] },
});

// Schema for a single block
const BLOCK_SCHEMA = Object.freeze({
  id:     { type:'string', required:true  },
  type:   { type:'string', required:true  },
  props:  { type:'object', required:true,  default:{} },
  styles: { type:'object', required:true,  default:{} },
});

// ─────────────────────────────────────────────────────────────────────────────
// 2. BLOCK CONTRACTS
//    Each block type defines allowed props, allowed styles, and defaults.
//    validateBlock / sanitizeBlock use these to enforce correctness.
// ─────────────────────────────────────────────────────────────────────────────

const BLOCK_CONTRACTS = Object.freeze({

  hero_centered: {
    props: {
      title:     { type:'string', default:'Build Something Amazing' },
      subtitle:  { type:'string', default:'The fastest way to launch your next idea.' },
      cta_text:  { type:'string', default:'Get Started Free' },
      cta_link:  { type:'string', default:'#' },
      cta2_text: { type:'string', default:'' },
      cta2_link: { type:'string', default:'#' },
      badge:     { type:'string', default:'' },
    },
    styles: {
      bg:         { type:'string', default:'gradient', enum:['gradient','solid','transparent'] },
      align:      { type:'string', default:'center',   enum:['left','center','right'] },
      padding:    { type:'string', default:'xl',        enum:['sm','md','lg','xl','2xl'] },
      text_color: { type:'color',  default:'#ffffff' },
    },
  },

  hero_split: {
    props: {
      title:    { type:'string', default:'Ship Faster Than Ever' },
      subtitle: { type:'string', default:'Automate your workflow.' },
      cta_text: { type:'string', default:'Start Free Trial' },
      cta_link: { type:'string', default:'#' },
      image:    { type:'string', default:'https://images.unsplash.com/photo-1551434678-e076c223a692?w=600&q=80' },
    },
    styles: {
      bg:         { type:'string', default:'#0f0f1a' },
      align:      { type:'string', default:'left', enum:['left','center','right'] },
      padding:    { type:'string', default:'xl',   enum:['sm','md','lg','xl','2xl'] },
      text_color: { type:'color',  default:'#ffffff' },
    },
  },

  hero_minimal: {
    props: {
      title:    { type:'string', default:'Simple. Fast. Powerful.' },
      subtitle: { type:'string', default:"Everything you need, nothing you don't." },
      cta_text: { type:'string', default:'Get Started' },
      cta_link: { type:'string', default:'#' },
    },
    styles: {
      bg:         { type:'string', default:'#ffffff' },
      align:      { type:'string', default:'center', enum:['left','center','right'] },
      padding:    { type:'string', default:'xl',     enum:['sm','md','lg','xl','2xl'] },
      text_color: { type:'color',  default:'#111111' },
    },
  },

  features_grid: {
    props: {
      title:    { type:'string', default:'Everything You Need' },
      subtitle: { type:'string', default:'Built for teams that move fast.' },
      items:    { type:'array',  default:[] },
    },
    styles: {
      bg:      { type:'string', default:'#f8f9ff' },
      padding: { type:'string', default:'xl', enum:['sm','md','lg','xl','2xl'] },
      cols:    { type:'number', default:3, min:1, max:4 },
    },
  },

  pricing_cards: {
    props: {
      title:    { type:'string', default:'Simple, Transparent Pricing' },
      subtitle: { type:'string', default:'No hidden fees. Cancel anytime.' },
      tiers:    { type:'array',  default:[] },
    },
    styles: {
      bg:      { type:'string', default:'#ffffff' },
      padding: { type:'string', default:'xl', enum:['sm','md','lg','xl','2xl'] },
    },
  },

  testimonials_grid: {
    props: {
      title: { type:'string', default:'Loved by Thousands' },
      items: { type:'array',  default:[] },
    },
    styles: {
      bg:      { type:'string', default:'#f8f9ff' },
      padding: { type:'string', default:'xl', enum:['sm','md','lg','xl','2xl'] },
    },
  },

  cta_banner: {
    props: {
      title:     { type:'string', default:'Ready to Get Started?' },
      subtitle:  { type:'string', default:'Join 10,000+ teams already using our platform.' },
      cta_text:  { type:'string', default:'Start Free Trial' },
      cta_link:  { type:'string', default:'#' },
      cta2_text: { type:'string', default:'' },
      cta2_link: { type:'string', default:'#' },
    },
    styles: {
      bg:         { type:'string', default:'gradient', enum:['gradient','solid','transparent'] },
      padding:    { type:'string', default:'lg',       enum:['sm','md','lg','xl','2xl'] },
      text_color: { type:'color',  default:'#ffffff' },
    },
  },

  faq_accordion: {
    props: {
      title: { type:'string', default:'Frequently Asked Questions' },
      items: { type:'array',  default:[] },
    },
    styles: {
      bg:      { type:'string', default:'#ffffff' },
      padding: { type:'string', default:'xl', enum:['sm','md','lg','xl','2xl'] },
    },
  },

  stats_row: {
    props: {
      items: { type:'array', default:[] },
    },
    styles: {
      bg:      { type:'string', default:'#ffffff' },
      padding: { type:'string', default:'lg', enum:['sm','md','lg','xl','2xl'] },
    },
  },

  contact_form: {
    props: {
      title:    { type:'string', default:'Get in Touch' },
      subtitle: { type:'string', default:"We'd love to hear from you." },
      cta_text: { type:'string', default:'Send Message' },
    },
    styles: {
      bg:      { type:'string', default:'#f8f9ff' },
      padding: { type:'string', default:'xl', enum:['sm','md','lg','xl','2xl'] },
    },
  },
});

// ─────────────────────────────────────────────────────────────────────────────
// 3. Schema validation helpers
// ─────────────────────────────────────────────────────────────────────────────

/** Check a single value against a field schema. Returns array of error strings. */
function _checkField(key, value, fieldSchema) {
  const errors = [];
  if (fieldSchema.required && (value === undefined || value === null || value === '')) {
    errors.push(`"${key}" is required`);
    return errors;
  }
  if (value === undefined || value === null) return errors; // optional, missing is fine

  if (fieldSchema.type === 'string' && typeof value !== 'string') {
    errors.push(`"${key}" must be a string, got ${typeof value}`);
  }
  if (fieldSchema.type === 'number' && typeof value !== 'number') {
    errors.push(`"${key}" must be a number, got ${typeof value}`);
  }
  if (fieldSchema.type === 'array' && !Array.isArray(value)) {
    errors.push(`"${key}" must be an array`);
  }
  if (fieldSchema.type === 'object' && (typeof value !== 'object' || Array.isArray(value))) {
    errors.push(`"${key}" must be an object`);
  }
  if (fieldSchema.type === 'color' && typeof value === 'string' && !/^#[0-9a-fA-F]{3,8}$/.test(value)) {
    errors.push(`"${key}" must be a hex color, got "${value}"`);
  }
  if (fieldSchema.enum && !fieldSchema.enum.includes(value)) {
    errors.push(`"${key}" must be one of [${fieldSchema.enum.join(', ')}], got "${value}"`);
  }
  if (fieldSchema.min !== undefined && typeof value === 'number' && value < fieldSchema.min) {
    errors.push(`"${key}" must be >= ${fieldSchema.min}`);
  }
  if (fieldSchema.max !== undefined && typeof value === 'number' && value > fieldSchema.max) {
    errors.push(`"${key}" must be <= ${fieldSchema.max}`);
  }
  return errors;
}

/** Auto-fix a value to match its field schema. Returns the fixed value. */
function _fixField(value, fieldSchema) {
  // Wrong type — return default
  if (fieldSchema.type === 'string'  && typeof value !== 'string')  return fieldSchema.default ?? '';
  if (fieldSchema.type === 'number'  && typeof value !== 'number')  return fieldSchema.default ?? 0;
  if (fieldSchema.type === 'array'   && !Array.isArray(value))      return fieldSchema.default ?? [];
  if (fieldSchema.type === 'object'  && typeof value !== 'object')  return fieldSchema.default ?? {};
  if (fieldSchema.type === 'color'   && !/^#[0-9a-fA-F]{3,8}$/.test(String(value))) return fieldSchema.default ?? '#000000';
  // Enum violation — return default
  if (fieldSchema.enum && !fieldSchema.enum.includes(value)) return fieldSchema.default ?? fieldSchema.enum[0];
  // Range clamp
  if (fieldSchema.min !== undefined && typeof value === 'number' && value < fieldSchema.min) return fieldSchema.min;
  if (fieldSchema.max !== undefined && typeof value === 'number' && value > fieldSchema.max) return fieldSchema.max;
  return value;
}

// ─────────────────────────────────────────────────────────────────────────────
// 4. Public API
// ─────────────────────────────────────────────────────────────────────────────

/**
 * validateConfig(cfg) — validate and auto-repair a full config object.
 * Returns { config, errors } where config is always safe to use.
 */
function validateConfig(cfg) {
  const errors = [];

  if (!cfg || typeof cfg !== 'object') {
    errors.push('Config is not an object — using default');
    return { config: JSON.parse(JSON.stringify(typeof DEFAULT_CONFIG !== 'undefined' ? DEFAULT_CONFIG : {})), errors };
  }

  const out = JSON.parse(JSON.stringify(cfg));

  // Validate + fix top-level scalars
  for (const [key, fieldSchema] of Object.entries(CONFIG_SCHEMA)) {
    if (fieldSchema.type === 'object') continue; // handled below
    const fieldErrors = _checkField(key, out[key], fieldSchema);
    if (fieldErrors.length) {
      errors.push(...fieldErrors);
      out[key] = _fixField(out[key], fieldSchema);
      if (out[key] === undefined) out[key] = fieldSchema.default;
    }
  }

  // Validate pages
  if (!out.pages || typeof out.pages !== 'object' || Array.isArray(out.pages)) {
    errors.push('"pages" is missing or invalid — using default');
    out.pages = typeof DEFAULT_CONFIG !== 'undefined'
      ? JSON.parse(JSON.stringify(DEFAULT_CONFIG.pages))
      : {};
  } else {
    for (const [pageKey, page] of Object.entries(out.pages)) {
      if (!page || typeof page !== 'object') {
        errors.push(`Page "${pageKey}" is invalid — removing`);
        delete out.pages[pageKey];
        continue;
      }
      // Fix each page field
      for (const [fk, fs] of Object.entries(PAGE_SCHEMA)) {
        const fe = _checkField(fk, page[fk], fs);
        if (fe.length) {
          errors.push(`Page "${pageKey}".${fk}: ${fe.join(', ')}`);
          page[fk] = _fixField(page[fk], fs);
          if (page[fk] === undefined) page[fk] = fs.default;
        }
      }
      // Sanitize blocks
      page.blocks = (page.blocks || [])
        .filter(b => b && typeof b === 'object')
        .map(b => sanitizeBlock(b));
    }
    if (Object.keys(out.pages).length === 0) {
      errors.push('No valid pages — adding default home page');
      out.pages.home = { title:'Home', file:'index.html', slug:'/home', sections:['hero'], blocks:[] };
    }
  }

  // Ensure features object
  if (!out.features || typeof out.features !== 'object') {
    out.features = typeof DEFAULT_CONFIG !== 'undefined'
      ? JSON.parse(JSON.stringify(DEFAULT_CONFIG.features))
      : {};
  }

  // Ensure content arrays
  if (!out.content || typeof out.content !== 'object') {
    out.content = typeof DEFAULT_CONFIG !== 'undefined'
      ? JSON.parse(JSON.stringify(DEFAULT_CONFIG.content))
      : {};
  } else {
    const CONTENT_ARRAYS = ['stats','features','testimonials','services','team','faq','pricing','blog_posts','portfolio_items'];
    for (const k of CONTENT_ARRAYS) {
      if (!Array.isArray(out.content[k])) {
        errors.push(`content.${k} is not an array — resetting`);
        out.content[k] = typeof DEFAULT_CONFIG !== 'undefined'
          ? JSON.parse(JSON.stringify(DEFAULT_CONFIG.content[k] || []))
          : [];
      }
    }
  }

  return { config: out, errors };
}

/**
 * validateBlock(block) — check a block against its contract.
 * Returns { valid, errors }.
 */
function validateBlock(block) {
  const errors = [];

  if (!block || typeof block !== 'object') {
    return { valid: false, errors: ['Block is not an object'] };
  }

  // Check required block fields
  for (const [key, fs] of Object.entries(BLOCK_SCHEMA)) {
    const fe = _checkField(key, block[key], fs);
    if (fe.length) errors.push(...fe);
  }

  if (!block.type) return { valid: false, errors: ['Block has no type', ...errors] };

  const contract = BLOCK_CONTRACTS[block.type];
  if (!contract) {
    errors.push(`Unknown block type: "${block.type}"`);
    return { valid: false, errors };
  }

  // Check props
  for (const [key, fs] of Object.entries(contract.props)) {
    const fe = _checkField(key, block.props?.[key], fs);
    if (fe.length) errors.push(`props.${key}: ${fe.join(', ')}`);
  }

  // Check styles
  for (const [key, fs] of Object.entries(contract.styles)) {
    const fe = _checkField(key, block.styles?.[key], fs);
    if (fe.length) errors.push(`styles.${key}: ${fe.join(', ')}`);
  }

  return { valid: errors.length === 0, errors };
}

/**
 * sanitizeBlock(block) — return a clean block with all required fields.
 * Never throws. Always returns a usable block object.
 */
function sanitizeBlock(block) {
  if (!block || typeof block !== 'object') {
    return { id: _makeId(), type: 'hero_centered', props: {}, styles: {} };
  }

  const out = {
    id:     typeof block.id === 'string' && block.id ? block.id : _makeId(),
    type:   typeof block.type === 'string' && block.type ? block.type : 'hero_centered',
    props:  (block.props  && typeof block.props  === 'object' && !Array.isArray(block.props))  ? { ...block.props  } : {},
    styles: (block.styles && typeof block.styles === 'object' && !Array.isArray(block.styles)) ? { ...block.styles } : {},
  };

  const contract = BLOCK_CONTRACTS[out.type];
  if (!contract) return out; // unknown type — keep as-is, render will show error

  // Fill missing props from contract defaults
  for (const [key, fs] of Object.entries(contract.props)) {
    if (out.props[key] === undefined || out.props[key] === null) {
      out.props[key] = fs.default;
    } else {
      out.props[key] = _fixField(out.props[key], fs);
    }
  }

  // Fill missing styles from contract defaults
  for (const [key, fs] of Object.entries(contract.styles)) {
    if (out.styles[key] === undefined || out.styles[key] === null) {
      out.styles[key] = fs.default;
    } else {
      out.styles[key] = _fixField(out.styles[key], fs);
    }
  }

  return out;
}

/**
 * updateConfig(cfg, path, value) — safe path-based setter.
 * path: dot-separated string, e.g. "pages.home.title" or "features.dark_mode"
 * Returns a new config object (does not mutate the original).
 * Throws if the path is invalid or the value fails schema validation.
 */
function updateConfig(cfg, path, value) {
  if (!path || typeof path !== 'string') throw new Error('updateConfig: path must be a non-empty string');

  const parts = path.split('.');
  const out   = JSON.parse(JSON.stringify(cfg)); // deep clone
  let   node  = out;

  // Walk to the parent of the target key
  for (let i = 0; i < parts.length - 1; i++) {
    const p = parts[i];
    if (node[p] === undefined || node[p] === null) {
      node[p] = {};
    }
    if (typeof node[p] !== 'object' || Array.isArray(node[p])) {
      throw new Error(`updateConfig: "${parts.slice(0, i + 1).join('.')}" is not an object`);
    }
    node = node[p];
  }

  const lastKey = parts[parts.length - 1];

  // Validate against schema if we have a rule for this top-level key
  const topKey = parts[0];
  if (parts.length === 1 && CONFIG_SCHEMA[topKey]) {
    const fe = _checkField(topKey, value, CONFIG_SCHEMA[topKey]);
    if (fe.length) {
      // Auto-fix rather than throw
      value = _fixField(value, CONFIG_SCHEMA[topKey]);
    }
  }

  // Sanitize strings
  if (typeof value === 'string') {
    value = value.slice(0, 5000); // hard cap
  }

  node[lastKey] = value;
  return out;
}

/**
 * updateBlockProp(cfg, blockId, key, value) — safe block prop setter.
 * Validates key against the block's contract. Returns new config.
 */
function updateBlockProp(cfg, blockId, key, value) {
  const out = JSON.parse(JSON.stringify(cfg));
  const blk = _findBlock(out, blockId);
  if (!blk) throw new Error(`updateBlockProp: block "${blockId}" not found`);

  const contract = BLOCK_CONTRACTS[blk.type];
  if (contract?.props[key]) {
    value = _fixField(value, contract.props[key]);
  }
  if (typeof value === 'string') value = value.slice(0, 5000);

  blk.props[key] = value;
  return out;
}

/**
 * updateBlockStyle(cfg, blockId, key, value) — safe block style setter.
 * Validates key against the block's contract. Returns new config.
 */
function updateBlockStyle(cfg, blockId, key, value) {
  const out = JSON.parse(JSON.stringify(cfg));
  const blk = _findBlock(out, blockId);
  if (!blk) throw new Error(`updateBlockStyle: block "${blockId}" not found`);

  const contract = BLOCK_CONTRACTS[blk.type];
  if (contract?.styles[key]) {
    value = _fixField(value, contract.styles[key]);
  }

  blk.styles[key] = value;
  return out;
}

// ─────────────────────────────────────────────────────────────────────────────
// 5. Internal helpers
// ─────────────────────────────────────────────────────────────────────────────

function _makeId() {
  return 'blk_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
}

/** Find a block by ID across all pages. Returns the block object (mutable ref). */
function _findBlock(cfg, blockId) {
  for (const page of Object.values(cfg.pages || {})) {
    const blk = (page.blocks || []).find(b => b.id === blockId);
    if (blk) return blk;
  }
  return null;
}
