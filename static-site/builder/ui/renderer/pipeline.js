/**
 * renderer/pipeline.js — Block render pipeline.
 *
 * renderPipeline(blockCfg, theme, opts) runs a block through:
 *   1. validate   — check block contract (schema.js)
 *   2. sanitize   — fill missing fields with defaults
 *   3. applyTheme — inject theme vars into props/styles
 *   4. hookBefore — call beforeRender hooks (plugins can modify)
 *   5. render     — call block's render() function
 *   6. hookAfter  — call afterRender hooks (plugins can inject)
 *   7. optimize   — add lazy loading, defer scripts
 *   8. cache      — store fingerprinted result
 *
 * The pipeline is deterministic: same input → same output.
 * Cache key = SHA-256(blockId + JSON(props) + JSON(styles) + JSON(theme)).
 *
 * Exports:
 *   renderPipeline(blockCfg, theme, opts) → string (HTML)
 *   clearRenderCache()
 *   getRenderStats()
 */
'use strict';

// ── Render cache ──────────────────────────────────────────────────────────────
const _renderCache = new Map();
const _MAX_CACHE   = 200;
const _stats       = { hits: 0, misses: 0, errors: 0, total: 0 };

function _cacheKey(blockCfg, theme) {
  // Fast fingerprint: JSON of the parts that affect output
  const parts = [
    blockCfg.id   || '',
    blockCfg.type || '',
    JSON.stringify(blockCfg.props  || {}),
    JSON.stringify(blockCfg.styles || {}),
    (theme?.primary   || ''),
    (theme?.secondary || ''),
  ];
  return parts.join('|');
}

function _cacheGet(key) {
  const entry = _renderCache.get(key);
  if (!entry) return null;
  _stats.hits++;
  return entry.html;
}

function _cacheSet(key, html) {
  if (_renderCache.size >= _MAX_CACHE) {
    // Evict oldest
    _renderCache.delete(_renderCache.keys().next().value);
  }
  _renderCache.set(key, { html, ts: Date.now() });
}

// ── Lazy loading + script defer (mirrors optimize.js logic, client-side) ──────
function _addLazyLoading(html) {
  return html.replace(/<img\b([^>]*)>/gi, (match, attrs) => {
    if (/loading=/i.test(attrs)) return match;
    return `<img${attrs} loading="lazy">`;
  });
}

function _deferScripts(html) {
  return html.replace(/<script\b([^>]*)>/gi, (match, attrs) => {
    if (/defer|async|src=/i.test(attrs) === false) return match;
    if (/defer|async/i.test(attrs)) return match;
    return `<script defer${attrs}>`;
  });
}

// ── Error fallback HTML ───────────────────────────────────────────────────────
function _errorBlock(blockId, type, message) {
  return `<section data-block="${blockId}" data-error="true" style="padding:1.5rem;background:#fef2f2;border:2px dashed #fca5a5;border-radius:.75rem;color:#991b1b;font-family:monospace;font-size:.85rem">
  <strong>[Block Error: ${type}]</strong><br>${message}
</section>`;
}

// ── Main pipeline ─────────────────────────────────────────────────────────────

/**
 * renderPipeline(blockCfg, theme, opts) → HTML string
 *
 * @param {object} blockCfg  - { id, type, props, styles }
 * @param {object} theme     - { primary, secondary, font, ... }
 * @param {object} opts      - { skipCache, debug, pluginCtx }
 */
async function renderPipeline(blockCfg, theme = {}, opts = {}) {
  _stats.total++;
  const t0 = performance.now();

  // ── 1. Validate ─────────────────────────────────────────────────────────────
  if (!blockCfg?.type) {
    _stats.errors++;
    return _errorBlock(blockCfg?.id || '?', '?', 'Block has no type');
  }

  // ── 2. Sanitize ──────────────────────────────────────────────────────────────
  let block = blockCfg;
  if (typeof sanitizeBlock === 'function') {
    try {
      block = sanitizeBlock(blockCfg);
    } catch (e) {
      console.warn('[Pipeline] sanitizeBlock failed:', e.message);
    }
  }

  // ── 3. Cache check ───────────────────────────────────────────────────────────
  const cacheKey = _cacheKey(block, theme);
  if (!opts.skipCache) {
    const cached = _cacheGet(cacheKey);
    if (cached !== null) return cached;
  }
  _stats.misses++;

  // ── 4. applyTheme — inject theme into styles ──────────────────────────────
  const themedBlock = _applyThemeToBlock(block, theme);

  // ── 5. beforeRender hook ─────────────────────────────────────────────────
  const hookCtx = { block: themedBlock, theme, opts, html: null };
  if (typeof Hooks !== 'undefined') {
    await Hooks.call('beforeRender', hookCtx);
  }
  // A hook can short-circuit by setting hookCtx.html
  if (hookCtx.html !== null) {
    _cacheSet(cacheKey, hookCtx.html);
    return hookCtx.html;
  }

  // ── 6. Render ────────────────────────────────────────────────────────────
  let html;
  try {
    if (typeof renderBlock === 'function') {
      html = renderBlock(hookCtx.block, theme);
    } else {
      html = _errorBlock(block.id, block.type, 'renderBlock() not available');
    }
  } catch (e) {
    _stats.errors++;
    html = _errorBlock(block.id, block.type, e.message);
  }

  // ── 7. afterRender hook ──────────────────────────────────────────────────
  hookCtx.html = html;
  if (typeof Hooks !== 'undefined') {
    await Hooks.call('afterRender', hookCtx);
    html = hookCtx.html;
  }

  // ── 8. Plugin render fragments ───────────────────────────────────────────
  if (typeof PluginLoader !== 'undefined') {
    const fragments = PluginLoader.renderAll({ block: hookCtx.block, theme });
    if (fragments.length) {
      // Inject plugin fragments before </section> or at end
      html = html.replace(/<\/section>/, fragments.join('\n') + '</section>') || html + fragments.join('\n');
    }
  }

  // ── 9. Optimize ──────────────────────────────────────────────────────────
  html = _addLazyLoading(html);

  // ── 10. Cache ────────────────────────────────────────────────────────────
  _cacheSet(cacheKey, html);

  if (opts.debug) {
    const ms = Math.round(performance.now() - t0);
    console.debug(`[Pipeline] ${block.type}#${block.id} rendered in ${ms}ms`);
  }

  return html;
}

function _applyThemeToBlock(block, theme) {
  if (!theme?.primary) return block;
  // Deep clone to avoid mutating the original
  const b = JSON.parse(JSON.stringify(block));
  // Replace 'gradient' bg with actual gradient string
  if (b.styles?.bg === 'gradient') {
    b.styles._resolvedBg = `linear-gradient(135deg,${theme.primary},${theme.secondary || theme.primary})`;
  }
  return b;
}

// ── Render a full page (array of blocks) ─────────────────────────────────────

/**
 * renderPage(blocks, theme, opts) → HTML string
 * Renders all blocks in a page sequentially.
 */
async function renderPage(blocks = [], theme = {}, opts = {}) {
  const parts = await Promise.all(
    blocks.map(b => renderPipeline(b, theme, opts).catch(e => _errorBlock(b?.id, b?.type, e.message)))
  );
  return parts.join('\n');
}

// ── Cache management ──────────────────────────────────────────────────────────

function clearRenderCache() {
  _renderCache.clear();
}

function getRenderStats() {
  return {
    ..._stats,
    cacheSize:   _renderCache.size,
    hitRate:     _stats.total > 0 ? Math.round(_stats.hits / _stats.total * 100) : 0,
  };
}
