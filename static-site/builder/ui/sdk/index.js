/**
 * sdk/index.js — Public SDK for plugin and block authors.
 *
 * Exposes a stable, versioned API surface.
 * Internal implementation details are hidden.
 *
 * Usage (in a plugin file):
 *   const { createBlock, registerPlugin, extendTheme, registerHook } = WBS_SDK;
 *
 * Or as a module:
 *   import WBS_SDK from './sdk/index.js';
 */
'use strict';

const WBS_SDK = (() => {

  const VERSION = '1.0.0';

  // ── Block authoring ───────────────────────────────────────────────────────

  /**
   * createBlock(type, props, styles) → block config object
   * Convenience wrapper around the global createBlock() from blocks.js.
   */
  function createBlock(type, props = {}, styles = {}) {
    if (typeof window.createBlock === 'function') {
      const blk = window.createBlock(type);
      if (blk) {
        Object.assign(blk.props,  props);
        Object.assign(blk.styles, styles);
        return blk;
      }
    }
    // Fallback: create minimal block
    return {
      id:     'blk_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
      type,
      props:  { ...props },
      styles: { ...styles },
    };
  }

  /**
   * registerBlock(definition) — Register a custom block type.
   * definition must match the BLOCKS array contract in blocks.js.
   */
  function registerBlock(definition) {
    if (!definition?.type) throw new Error('registerBlock: definition.type is required');
    if (!definition?.render) throw new Error('registerBlock: definition.render() is required');
    if (typeof BLOCKS !== 'undefined' && Array.isArray(BLOCKS)) {
      // Remove existing definition with same type (allow override)
      const idx = BLOCKS.findIndex(b => b.type === definition.type);
      if (idx >= 0) BLOCKS.splice(idx, 1);
      BLOCKS.push(definition);
    } else {
      console.warn('[SDK] BLOCKS registry not available — block not registered');
    }
  }

  // ── Plugin authoring ──────────────────────────────────────────────────────

  /**
   * registerPlugin(plugin) — Register and optionally enable a plugin.
   * plugin must match the PluginLoader contract.
   */
  function registerPlugin(plugin, enableImmediately = false, settings = {}) {
    if (typeof PluginLoader === 'undefined') {
      console.warn('[SDK] PluginLoader not available');
      return;
    }
    PluginLoader.register(plugin);
    if (enableImmediately) PluginLoader.enable(plugin.id, settings);
  }

  // ── Hook authoring ────────────────────────────────────────────────────────

  /**
   * registerHook(hookName, fn, opts) — Register a hook handler.
   * Thin wrapper around Hooks.on().
   */
  function registerHook(hookName, fn, opts = {}) {
    if (typeof Hooks === 'undefined') {
      console.warn('[SDK] Hooks not available');
      return;
    }
    Hooks.on(hookName, fn, opts);
  }

  // ── Theme authoring ───────────────────────────────────────────────────────

  /**
   * extendTheme(preset) — Add a theme preset to the THEME_PRESETS array.
   * preset: { name, primary, secondary, bg, text }
   */
  function extendTheme(preset) {
    if (!preset?.name || !preset?.primary) throw new Error('extendTheme: name and primary are required');
    if (typeof THEME_PRESETS !== 'undefined' && Array.isArray(THEME_PRESETS)) {
      // THEME_PRESETS is frozen — we need to work around that
      console.warn('[SDK] THEME_PRESETS is frozen — theme preset not added at runtime. Add to theme.js instead.');
    }
    // Store in a mutable extension registry
    WBS_SDK._themeExtensions = WBS_SDK._themeExtensions || [];
    WBS_SDK._themeExtensions.push(preset);
  }

  // ── Event authoring ───────────────────────────────────────────────────────

  /**
   * onEvent(type, fn) — Subscribe to a builder event.
   * Returns unsubscribe function.
   */
  function onEvent(type, fn) {
    if (typeof Events === 'undefined') return () => {};
    return Events.on(type, fn);
  }

  /**
   * emitEvent(type, payload) — Emit a custom event.
   */
  function emitEvent(type, payload) {
    if (typeof Events === 'undefined') return;
    Events._emit?.(type, payload, 'sdk');
  }

  // ── Render pipeline ───────────────────────────────────────────────────────

  /**
   * renderBlock(blockCfg, theme) → Promise<string>
   * Run a block through the full render pipeline.
   */
  async function renderBlockSDK(blockCfg, theme = {}) {
    if (typeof renderPipeline === 'function') {
      return renderPipeline(blockCfg, theme);
    }
    if (typeof window.renderBlock === 'function') {
      return window.renderBlock(blockCfg, theme);
    }
    return `<!-- block:${blockCfg.type} -->`;
  }

  // ── Diagnostics ───────────────────────────────────────────────────────────

  /**
   * inspect() — Return a snapshot of the current SDK state.
   * Useful for debugging plugins.
   */
  function inspect() {
    return {
      version:  VERSION,
      plugins:  typeof PluginLoader !== 'undefined' ? PluginLoader.getAll() : [],
      hooks:    typeof Hooks        !== 'undefined' ? Hooks.inspect()       : {},
      blocks:   typeof BLOCKS       !== 'undefined' ? BLOCKS.map(b => b.type) : [],
      events:   typeof Events       !== 'undefined' ? Events.getLog(null, 20) : [],
      render:   typeof getRenderStats === 'function' ? getRenderStats()     : {},
    };
  }

  // ── Public surface ────────────────────────────────────────────────────────
  return {
    VERSION,
    createBlock,
    registerBlock,
    registerPlugin,
    registerHook,
    extendTheme,
    onEvent,
    emitEvent,
    renderBlock: renderBlockSDK,
    inspect,
    _themeExtensions: [],
  };
})();
