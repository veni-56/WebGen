/**
 * core/hooks.js — Synchronous + async hook system.
 *
 * Hooks are named extension points. Plugins register handlers;
 * the engine calls them in priority order.
 *
 * Usage:
 *   Hooks.on('beforeRender', (ctx) => { ctx.block.props.title += ' (modified)'; });
 *   await Hooks.call('beforeRender', ctx);
 *
 * Supported hooks:
 *   beforeBuild(ctx)    afterBuild(ctx)
 *   beforeRender(ctx)   afterRender(ctx)
 *   beforePublish(ctx)  afterPublish(ctx)
 *   beforeSave(ctx)     afterSave(ctx)
 *   onError(ctx)
 */
'use strict';

const Hooks = (() => {
  // Map<hookName, Array<{pluginId, fn, priority}>>
  const _registry = new Map();

  return {
    /**
     * Register a handler for a hook.
     * @param {string}   hookName  - e.g. 'beforeRender'
     * @param {Function} fn        - handler(ctx) → void | Promise<void>
     * @param {object}   opts      - { pluginId, priority (default 10) }
     */
    on(hookName, fn, { pluginId = 'core', priority = 10 } = {}) {
      if (!_registry.has(hookName)) _registry.set(hookName, []);
      _registry.get(hookName).push({ pluginId, fn, priority });
      // Keep sorted by priority descending
      _registry.get(hookName).sort((a, b) => b.priority - a.priority);
    },

    /**
     * Remove all handlers registered by a plugin.
     */
    off(pluginId) {
      for (const [name, handlers] of _registry) {
        _registry.set(name, handlers.filter(h => h.pluginId !== pluginId));
      }
    },

    /**
     * Call all handlers for a hook in priority order.
     * Handlers can mutate ctx. Errors are caught and logged.
     * @returns {Promise<object>} the (possibly mutated) ctx
     */
    async call(hookName, ctx = {}) {
      const handlers = _registry.get(hookName) || [];
      for (const { pluginId, fn } of handlers) {
        try {
          await fn(ctx);
        } catch (e) {
          console.error(`[Hook:${hookName}] Plugin "${pluginId}" threw:`, e);
          ctx._hookErrors = ctx._hookErrors || [];
          ctx._hookErrors.push({ hook: hookName, plugin: pluginId, error: e.message });
        }
      }
      return ctx;
    },

    /**
     * Synchronous version — for hooks that must not be async.
     */
    callSync(hookName, ctx = {}) {
      const handlers = _registry.get(hookName) || [];
      for (const { pluginId, fn } of handlers) {
        try {
          fn(ctx);
        } catch (e) {
          console.error(`[Hook:${hookName}] Plugin "${pluginId}" threw:`, e);
        }
      }
      return ctx;
    },

    /** List all registered hooks and their handler counts. */
    inspect() {
      const out = {};
      for (const [name, handlers] of _registry) {
        out[name] = handlers.map(h => ({ plugin: h.pluginId, priority: h.priority }));
      }
      return out;
    },

    /** Clear all hooks (used in tests). */
    clear() { _registry.clear(); },
  };
})();
