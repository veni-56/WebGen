/**
 * pipeline/build_pipeline.js — Staged build pipeline (client-side orchestration).
 *
 * Stages:
 *   1. validate   — schema + plugin validation
 *   2. normalize  — fill defaults, sanitize blocks
 *   3. render     — render all blocks via renderPipeline
 *   4. optimize   — lazy loading, asset versioning
 *   5. package    — assemble final HTML pages
 *   6. publish    — hand off to server API
 *
 * Each stage is timed, logged, and recoverable.
 * A stage failure does not crash the pipeline — it records the error
 * and either skips or uses a safe fallback.
 *
 * Usage:
 *   const result = await BuildPipeline.run(cfg, { mode: 'preview', page: 'home' });
 *   // result: { ok, stages, html, errors }
 */
'use strict';

const BuildPipeline = (() => {

  // ── Stage runner ──────────────────────────────────────────────────────────
  async function _runStage(name, fn, ctx) {
    const t0 = performance.now();
    ctx.stages[name] = { status: 'running', ms: 0, error: null };
    try {
      await fn(ctx);
      ctx.stages[name].status = 'done';
    } catch (e) {
      ctx.stages[name].status = 'error';
      ctx.stages[name].error  = e.message;
      ctx.errors.push({ stage: name, error: e.message });
      console.error(`[Pipeline:${name}]`, e);
    }
    ctx.stages[name].ms = Math.round(performance.now() - t0);
    if (typeof Logger !== 'undefined') {
      Logger.log('PREVIEW_BUILD', { stage: name, ms: ctx.stages[name].ms, ok: ctx.stages[name].status === 'done' });
    }
  }

  // ── Stage implementations ─────────────────────────────────────────────────

  async function _stageValidate(ctx) {
    // Schema validation
    if (typeof validateConfig === 'function') {
      const result = validateConfig(ctx.cfg);
      if (result.errors?.length) {
        ctx.validationErrors = result.errors;
        ctx.cfg = result.config;   // use repaired config
      }
    }
    // Plugin validation
    if (typeof PluginLoader !== 'undefined') {
      const pluginErrors = PluginLoader.validateAll(ctx.cfg);
      if (Object.keys(pluginErrors).length) {
        ctx.pluginErrors = pluginErrors;
      }
    }
    // beforeBuild hook
    if (typeof Hooks !== 'undefined') {
      await Hooks.call('beforeBuild', ctx);
    }
  }

  async function _stageNormalize(ctx) {
    // Ensure all blocks have IDs and valid props
    if (typeof sanitizeBlock === 'function') {
      for (const page of Object.values(ctx.cfg.pages || {})) {
        page.blocks = (page.blocks || []).map(b => {
          try { return sanitizeBlock(b); } catch(e) { return b; }
        });
      }
    }
  }

  async function _stageRender(ctx) {
    const theme = {
      primary:   ctx.cfg.primary_color   || '#6c63ff',
      secondary: ctx.cfg.secondary_color || '#f50057',
      font:      ctx.cfg.font            || 'Inter',
    };
    ctx.renderedPages = {};
    const targetPage = ctx.opts.page;

    for (const [pageKey, page] of Object.entries(ctx.cfg.pages || {})) {
      if (targetPage && pageKey !== targetPage) continue;
      const blocks = page.blocks || [];
      if (typeof renderPage === 'function') {
        ctx.renderedPages[pageKey] = await renderPage(blocks, theme, { debug: ctx.opts.debug });
      } else {
        ctx.renderedPages[pageKey] = blocks.map(b => `<!-- block:${b.type} -->`).join('\n');
      }
    }
  }

  async function _stageOptimize(ctx) {
    // afterRender hook (plugins can inject analytics, SEO tags, etc.)
    if (typeof Hooks !== 'undefined') {
      for (const [pageKey, html] of Object.entries(ctx.renderedPages || {})) {
        const hookCtx = { pageKey, html, cfg: ctx.cfg };
        await Hooks.call('afterRender', hookCtx);
        ctx.renderedPages[pageKey] = hookCtx.html;
      }
    }
  }

  async function _stagePackage(ctx) {
    // For preview: just return the rendered HTML for the target page
    const page = ctx.opts.page || Object.keys(ctx.renderedPages || {})[0];
    ctx.html = ctx.renderedPages?.[page] || '';
  }

  async function _stagePublish(ctx) {
    if (ctx.opts.mode !== 'publish') return;
    // beforePublish hook
    if (typeof Hooks !== 'undefined') {
      await Hooks.call('beforePublish', ctx);
    }
    // Actual publish is handled by the server — this stage just prepares
    ctx.readyToPublish = true;
  }

  // ── Public API ────────────────────────────────────────────────────────────

  return {
    /**
     * Run the full pipeline.
     * @param {object} cfg   - project config
     * @param {object} opts  - { mode: 'preview'|'publish', page, debug }
     * @returns {object}     - { ok, stages, html, errors, cfg }
     */
    async run(cfg, opts = {}) {
      const ctx = {
        cfg:    JSON.parse(JSON.stringify(cfg)),   // deep clone — never mutate original
        opts,
        stages: {},
        errors: [],
        html:   '',
        renderedPages: {},
      };

      await _runStage('validate',  _stageValidate,  ctx);
      await _runStage('normalize', _stageNormalize, ctx);
      await _runStage('render',    _stageRender,    ctx);
      await _runStage('optimize',  _stageOptimize,  ctx);
      await _runStage('package',   _stagePackage,   ctx);
      await _runStage('publish',   _stagePublish,   ctx);

      const ok = ctx.errors.length === 0;
      return { ok, stages: ctx.stages, html: ctx.html, errors: ctx.errors, cfg: ctx.cfg };
    },

    /** Run only the validate stage (for real-time feedback). */
    async validate(cfg) {
      const ctx = { cfg: JSON.parse(JSON.stringify(cfg)), opts: {}, stages: {}, errors: [] };
      await _runStage('validate', _stageValidate, ctx);
      return { errors: ctx.errors, validationErrors: ctx.validationErrors, pluginErrors: ctx.pluginErrors };
    },
  };
})();
