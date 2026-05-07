/**
 * core/plugin_loader.js — Frontend plugin registry and loader.
 *
 * Plugin contract:
 * {
 *   id:       string,          // unique, e.g. 'seo'
 *   name:     string,          // display name
 *   version:  string,          // semver
 *   hooks:    { [hookName]: fn },   // registered on load
 *   settings: { [key]: defaultValue },
 *   render(ctx):  string | null,   // inject HTML into page
 *   validate(cfg): string[],        // return array of error strings
 *   onEnable(settings):  void,
 *   onDisable():         void,
 * }
 *
 * Usage:
 *   PluginLoader.register(myPlugin);
 *   PluginLoader.enable('seo', { title_suffix: ' | My Site' });
 *   PluginLoader.disable('seo');
 *   PluginLoader.getEnabled();
 */
'use strict';

const PluginLoader = (() => {
  const _registry = new Map();   // id → plugin definition
  const _enabled  = new Map();   // id → { settings }
  const _errors   = new Map();   // id → last error

  return {
    /**
     * Register a plugin definition.
     * Safe to call multiple times (idempotent).
     */
    register(plugin) {
      if (!plugin?.id) { console.warn('[PluginLoader] Plugin missing id'); return; }
      _registry.set(plugin.id, plugin);
    },

    /**
     * Enable a plugin with optional settings.
     * Registers its hooks and calls onEnable.
     */
    enable(id, settings = {}) {
      const plugin = _registry.get(id);
      if (!plugin) { console.warn(`[PluginLoader] Unknown plugin: ${id}`); return false; }
      if (_enabled.has(id)) return true;   // already enabled

      const merged = { ...plugin.settings, ...settings };
      try {
        // Register hooks
        if (plugin.hooks && typeof Hooks !== 'undefined') {
          for (const [hookName, fn] of Object.entries(plugin.hooks)) {
            Hooks.on(hookName, fn, { pluginId: id });
          }
        }
        plugin.onEnable?.(merged);
        _enabled.set(id, { settings: merged });
        _errors.delete(id);
        return true;
      } catch (e) {
        _errors.set(id, e.message);
        console.error(`[PluginLoader] Failed to enable "${id}":`, e);
        return false;
      }
    },

    /**
     * Disable a plugin.
     * Removes its hooks and calls onDisable.
     */
    disable(id) {
      if (!_enabled.has(id)) return;
      const plugin = _registry.get(id);
      try {
        if (typeof Hooks !== 'undefined') Hooks.off(id);
        plugin?.onDisable?.();
      } catch (e) {
        console.error(`[PluginLoader] Error disabling "${id}":`, e);
      }
      _enabled.delete(id);
    },

    /** Update settings for an enabled plugin. */
    updateSettings(id, settings) {
      if (!_enabled.has(id)) return;
      const current = _enabled.get(id);
      _enabled.set(id, { settings: { ...current.settings, ...settings } });
      const plugin = _registry.get(id);
      plugin?.onEnable?.(_enabled.get(id).settings);
    },

    /** Get settings for an enabled plugin. */
    getSettings(id) {
      return _enabled.get(id)?.settings || {};
    },

    /** Return array of enabled plugin IDs. */
    getEnabled() {
      return [..._enabled.keys()];
    },

    /** Return all registered plugin definitions. */
    getAll() {
      return [..._registry.values()].map(p => ({
        id:      p.id,
        name:    p.name,
        version: p.version || '1.0.0',
        enabled: _enabled.has(p.id),
        error:   _errors.get(p.id) || null,
      }));
    },

    /**
     * Run render() on all enabled plugins.
     * Returns array of HTML strings to inject into the page.
     */
    renderAll(ctx) {
      const fragments = [];
      for (const [id] of _enabled) {
        const plugin = _registry.get(id);
        if (!plugin?.render) continue;
        try {
          const html = plugin.render({ ...ctx, settings: _enabled.get(id).settings });
          if (html) fragments.push(html);
        } catch (e) {
          console.error(`[PluginLoader] render() failed for "${id}":`, e);
        }
      }
      return fragments;
    },

    /**
     * Run validate() on all enabled plugins.
     * Returns { pluginId: [errors] }.
     */
    validateAll(cfg) {
      const results = {};
      for (const [id] of _enabled) {
        const plugin = _registry.get(id);
        if (!plugin?.validate) continue;
        try {
          const errors = plugin.validate(cfg);
          if (errors?.length) results[id] = errors;
        } catch (e) {
          results[id] = [e.message];
        }
      }
      return results;
    },

    /** Serialize enabled plugins + settings for storage in project config. */
    serialize() {
      const out = {};
      for (const [id, { settings }] of _enabled) {
        out[id] = settings;
      }
      return out;
    },

    /** Restore from serialized data (called on project load). */
    restore(data = {}) {
      for (const [id, settings] of Object.entries(data)) {
        if (_registry.has(id)) this.enable(id, settings);
      }
    },
  };
})();
