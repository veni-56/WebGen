/**
 * app.js — Website Builder Alpine.js component (refactored v5)
 *
 * Architecture:
 *   state.js  — DEFAULT_CONFIG, ALL_SECTIONS, TEMPLATES, validateConfig
 *   api.js    — all fetch calls, returns { ok, data, error }
 *   blocks.js — block registry, createBlock, renderBlock
 *   theme.js  — buildThemeCss, applyThemeToBuilder, pushThemeToIframe
 *   editor.js — styleEditorData, rich-text toolbar
 *   app.js    — Alpine component: wires everything together
 *
 * Sections:
 *   1. MSG constants
 *   2. Pure utility functions (clone, debounce, toast, hash, stripTags)
 *   3. Single theme helper (_applyTheme)
 *   4. Alpine component
 *      a. State declaration
 *      b. init()
 *      c. State mutation helpers (setState, updateSection, updateBlock)
 *      d. History (undo/redo)
 *      e. Project system
 *      f. Preview
 *      g. iframe bridge handler
 *      h. Sections
 *      i. Blocks
 *      j. Style editor
 *      k. Pages
 *      l. Content items
 *      m. Upload / media
 *      n. Export
 *      o. Persistence (localStorage)
 *      p. Private helpers
 */
'use strict';

// ─────────────────────────────────────────────────────────────────────────────
// 1. MSG — centralized postMessage type constants
//    Must match the MSG dict embedded in server.py's BRIDGE script.
// ─────────────────────────────────────────────────────────────────────────────
const MSG = Object.freeze({
  SELECT:        'wbs:select',
  DESELECT:      'wbs:deselect',
  ACTION:        'wbs:action',
  TEXT_EDIT:     'wbs:text-edit',
  IMAGE_CLICK:   'wbs:image-click',
  THEME:         'wbs:theme',
  HIGHLIGHT:     'wbs:highlight',
  REPLACE_IMAGE: 'wbs:replace-image',
  STYLE_UPDATE:  'wbs:style-update',
});

// ─────────────────────────────────────────────────────────────────────────────
// 2. Pure utility functions
// ─────────────────────────────────────────────────────────────────────────────

/** Deep-clone any JSON-serialisable value. */
const clone = v => JSON.parse(JSON.stringify(v));

/** Returns a debounced version of fn that fires after `ms` ms of silence. */
function debounce(fn, ms) {
  let t;
  return function (...a) { clearTimeout(t); t = setTimeout(() => fn.apply(this, a), ms); };
}

/**
 * throttleDebounce(fn, throttleMs, debounceMs)
 * Fires immediately if more than throttleMs has passed since last call,
 * otherwise debounces by debounceMs. Prevents both rapid-fire rebuilds
 * and stale previews after a burst of changes.
 */
function throttleDebounce(fn, throttleMs, debounceMs) {
  let lastCall = 0;
  let timer    = null;
  return function (...a) {
    const now = Date.now();
    clearTimeout(timer);
    if (now - lastCall >= throttleMs) {
      lastCall = now;
      fn.apply(this, a);
    } else {
      timer = setTimeout(() => { lastCall = Date.now(); fn.apply(this, a); }, debounceMs);
    }
  };
}

/**
 * Show a self-dismissing toast notification.
 * Returns a cancel function.
 */
function createToast(msg, type = 'success', ms = 3200) {
  const COLORS = { success:'#10b981', error:'#ef4444', info:'#6c63ff', warning:'#f59e0b' };
  // Inject keyframes once
  if (!document.getElementById('wbs-anim')) {
    const s = document.createElement('style');
    s.id = 'wbs-anim';
    s.textContent = '@keyframes wbsIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}@keyframes wbsOut{from{opacity:1}to{opacity:0;transform:translateY(6px)}}';
    document.head.appendChild(s);
  }
  const el = document.createElement('div');
  el.style.cssText = [
    'position:fixed;bottom:1.5rem;right:1.5rem;z-index:99999',
    'padding:.7rem 1.2rem;border-radius:.75rem',
    'font-size:.875rem;font-weight:600;color:#fff',
    `background:${COLORS[type] || COLORS.success}`,
    'box-shadow:0 8px 24px rgba(0,0,0,.2)',
    'animation:wbsIn .25s ease;pointer-events:none',
    'max-width:320px;line-height:1.4',
  ].join(';');
  el.textContent = msg;
  document.body.appendChild(el);
  const dismiss = () => {
    el.style.animation = 'wbsOut .25s ease forwards';
    setTimeout(() => el.remove(), 260);
  };
  const timer = setTimeout(dismiss, ms);
  return () => { clearTimeout(timer); dismiss(); };
}

/**
 * FNV-1a 32-bit hash of a config object.
 * Used to skip autosave when nothing has changed.
 */
function cfgHash(cfg) {
  const s = JSON.stringify(cfg, Object.keys(cfg).sort());
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h.toString(16);
}

/** Strip HTML tags — client-side guard before server sanitises. */
function stripTags(s) {
  return String(s || '').replace(/<[^>]*>/g, '').slice(0, 2000);
}

// ─────────────────────────────────────────────────────────────────────────────
// 3. Single theme helper
//    All theme application goes through here — no more scattered calls.
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Apply theme to:
 *   a) the builder UI (CSS vars on :root)
 *   b) the preview iframe (via postMessage)
 *
 * Uses theme.js if loaded, falls back to minimal inline implementation.
 */
function _applyTheme(cfg, frame) {
  const primary   = cfg.primary_color   || '#6c63ff';
  const secondary = cfg.secondary_color || '#f50057';
  const font      = cfg.font            || 'Inter';

  if (typeof applyThemeToBuilder === 'function') {
    // theme.js is loaded — use full shade generation
    applyThemeToBuilder({ primary, secondary, font });
  } else {
    // Minimal fallback
    const toRgb = h => [parseInt(h.slice(1,3),16), parseInt(h.slice(3,5),16), parseInt(h.slice(5,7),16)];
    const [pr,pg,pb] = toRgb(primary);
    const [sr,sg,sb] = toRgb(secondary);
    let el = document.getElementById('wbs-builder-theme') || document.getElementById('wbs-theme');
    if (!el) { el = document.createElement('style'); el.id = 'wbs-builder-theme'; document.head.appendChild(el); }
    el.textContent = `:root{--primary:${primary};--secondary:${secondary};--primary-rgb:${pr},${pg},${pb};--secondary-rgb:${sr},${sg},${sb}}`;
    let fl = document.getElementById('wbs-font');
    if (!fl) { fl = document.createElement('link'); fl.id = 'wbs-font'; fl.rel = 'stylesheet'; document.head.appendChild(fl); }
    fl.href = `https://fonts.googleapis.com/css2?family=${font.replace(/ /g,'+')}:wght@400;500;600;700;800&display=swap`;
  }

  if (frame) {
    try {
      const css = typeof buildThemeCss === 'function'
        ? buildThemeCss({ primary, secondary, font })
        : `:root{--primary:${primary};--secondary:${secondary}}`;
      frame.contentWindow.postMessage({ type: MSG.THEME, css }, '*');
    } catch (_) {}
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 4. Alpine component
// ─────────────────────────────────────────────────────────────────────────────

document.addEventListener('alpine:init', () => {
  Alpine.data('builder', () => ({

    // ── 4a. State ─────────────────────────────────────────────────────────────

    // Core config (the single source of truth for the generated site)
    cfg: null,   // set in init() after validation

    // UI tabs
    activeTab:    'Setup',
    contentTab:   'Features',
    sectionPage:  'home',

    // Preview
    previewPage:   'home',
    previewDevice: 'desktop',
    previewMode:   'srcdoc',   // 'srcdoc' | 'url'
    previewUrl:    '',
    buildMs:       0,
    buildError:    '',
    _lastPreviewKey: '',       // prevents redundant rebuilds

    // Selection
    selectedSection:     null,
    selectedSectionName: '',
    selectedBlockId:     null,

    // Sections (derived from cfg.pages[sectionPage].sections, kept in sync)
    currentSections: [],

    // Hidden sections per page: { pageKey: Set<sectionName> }
    hiddenSections: {},

    // Disabled pages (excluded from export/preview)
    disabledPages: [],

    // Modals / panels
    showTemplates:    false,
    showBlockLibrary: false,
    showStyleEditor:  false,
    showPageManager:  false,
    showImageUpload:  false,

    // Block library filter
    blockFilter: 'All',

    // Style editor — mirrors selStyles in editor.js
    selStyles: {
      bgType:'solid', bgColor:'#ffffff', textColor:'#111827',
      fontSize:'1rem', fontWeight:'400', lineHeight:'1.6', textAlign:'left',
      paddingTop:'4rem', paddingBottom:'4rem', paddingLeft:'2rem', paddingRight:'2rem',
      marginTop:'0', marginBottom:'0',
      borderWidth:'0', borderColor:'#e5e7eb', borderRadius:'0',
      shadow:'none',
    },

    // Upload / media
    uploadTarget:   null,   // { section, src } — image being replaced
    uploadedImages: [],     // [{ url, filename }]

    // Export
    exportMode: 'static',

    // Templates (from state.js)
    templates:         typeof TEMPLATES       !== 'undefined' ? TEMPLATES       : [],
    availableSections: typeof ALL_SECTIONS    !== 'undefined' ? ALL_SECTIONS    : [],
    allBlocks:         typeof BLOCKS          !== 'undefined' ? BLOCKS          : [],
    blockCategories:   typeof BLOCK_CATEGORIES !== 'undefined' ? BLOCK_CATEGORIES : [],
    themePresets:      typeof THEME_PRESETS   !== 'undefined' ? THEME_PRESETS   : [],

    // Project system
    projects:        [],
    currentProject:  null,
    projectId:       'default',
    publishUrl:      '',
    publishVersions: [],
    currentUser:     null,

    // Async / loading flags
    previewing:  false,
    saving:      false,
    exporting:   false,
    uploading:   false,
    publishing:  false,
    autoSaving:  false,

    // History (undo/redo)
    _history:    [],
    _historyIdx: -1,
    get canUndo() { return this._historyIdx > 0; },
    get canRedo() { return this._historyIdx < this._history.length - 1; },

    // Autosave dedup
    _lastSavedHash: '',

    // Toast cancel handle
    _rmToast: null,

    // Drag-and-drop
    _dragIdx: null,

    // Debug mode (Ctrl+Shift+D to toggle)
    debugMode: false,
    // Dev panel state
    devLogs:      [],
    devLastApi:   '',
    devLastBuild: 0,
    devReport:    null,

    // ── 4b. init() ────────────────────────────────────────────────────────────

    init() {
      // Load and validate config from localStorage (or use default)
      const raw = this._loadLocal();

      // Use schema.js validateConfig if available (returns { config, errors })
      // otherwise fall back to state.js validateConfig (returns config directly)
      if (typeof BLOCK_CONTRACTS !== 'undefined') {
        // schema.js is loaded — full validation
        const result = validateConfig(raw);
        this.cfg = result.config;
        if (result.errors?.length) {
          Logger.log('CONFIG_ERROR', { source: 'init', errors: result.errors });
        }
      } else {
        this.cfg = typeof validateConfig === 'function'
          ? validateConfig(raw)
          : (raw || JSON.parse(JSON.stringify(DEFAULT_CONFIG)));
      }

      this._pushHistory();
      this._syncSectionPage();
      _applyTheme(this.cfg, null);

      // Preview: throttle at 1s (fires immediately if idle), debounce at 400ms
      this.debouncedPreview  = throttleDebounce(() => this._buildPreview(), 1000, 400);
      this.debouncedAutoSave = debounce(() => this._autoSave(), 2000);

      // iframe bridge messages
      window.addEventListener('message', e => this._onFrameMessage(e));

      // Global error boundary — catch unhandled promise rejections
      window.addEventListener('unhandledrejection', ev => {
        const msg = ev.reason?.message || String(ev.reason) || 'Unknown error';
        Logger.log('CONFIG_ERROR', { source: 'unhandledrejection', msg });
        this.buildError = msg;
        ev.preventDefault();
      });

      // Keyboard shortcuts
      document.addEventListener('keydown', e => {
        const mod = e.ctrlKey || e.metaKey;
        if (mod && !e.shiftKey && e.key === 'z') { e.preventDefault(); this.undo(); }
        if (mod && (e.key === 'y' || (e.shiftKey && e.key === 'z'))) { e.preventDefault(); this.redo(); }
        if (mod && e.key === 's') { e.preventDefault(); this.saveProject(); }
        if (mod && e.shiftKey && e.key === 'D') {
          e.preventDefault();
          this.debugMode = !this.debugMode;
          if (typeof Logger !== 'undefined') {
            this.debugMode ? Logger.enable() : Logger.disable();
            this.devLogs = Logger.getLogs();
          }
        }
        if (e.key === 'Escape') { this.selectedSection = null; this.selectedSectionName = ''; this.showStyleEditor = false; }
      });

      // Load projects from backend (non-blocking)
      this.loadProjects();

      // Wire Events system — emit snapshot on every commit
      if (typeof Events !== 'undefined') {
        Events.onAny(e => {
          if (this.debugMode && typeof DevTools !== 'undefined') {
            this.devReport = DevTools.getReport(this.cfg);
          }
        });
      }

      // Restore plugins from config
      if (typeof PluginLoader !== 'undefined' && this.cfg.plugins) {
        PluginLoader.restore(this.cfg.plugins);
      }

      // Check auth — redirect to login if not authenticated
      API.me().then(r => {
        if (!r.ok) { window.location.href = '/login'; return; }
        this.currentUser = r.data;
      });

      // Initial preview after a short delay (lets Alpine finish rendering)
      setTimeout(() => this._buildPreview(), 300);
    },

    // ── 4c. State mutation helpers ────────────────────────────────────────────

    /**
     * setState(patch) — merge a partial object into cfg using safe path updates.
     * Each key in patch is applied via updateConfig() for schema validation.
     */
    setState(patch) {
      let cfg = this.cfg;
      for (const [key, value] of Object.entries(patch)) {
        try {
          cfg = typeof updateConfig === 'function'
            ? updateConfig(cfg, key, value)
            : { ...cfg, [key]: value };
          Logger.log('STATE_UPDATE', { path: key, value });
        } catch (e) {
          Logger.log('CONFIG_ERROR', { path: key, error: e.message });
          this._toast(`Invalid value for "${key}"`, 'warning');
        }
      }
      this.cfg = cfg;
      this._commit();
    },

    /**
     * updateSection(pageKey, idx, newName) — replace a section name at index.
     */
    updateSection(pageKey, idx, newName) {
      const page = this.cfg.pages[pageKey];
      if (!page || !Array.isArray(page.sections)) return;
      try {
        this.cfg = typeof updateConfig === 'function'
          ? updateConfig(this.cfg, `pages.${pageKey}.sections.${idx}`, newName)
          : (() => { page.sections[idx] = newName; return this.cfg; })();
        if (pageKey === this.sectionPage) this._syncSectionPage();
        Logger.log('STATE_UPDATE', { path: `pages.${pageKey}.sections[${idx}]`, value: newName });
        this._commit();
      } catch (e) {
        Logger.log('CONFIG_ERROR', { path: `pages.${pageKey}.sections`, error: e.message });
      }
    },

    /**
     * updateBlock(pageKey, blockId, propPatch) — safe block prop update.
     * Uses schema.js updateBlockProp if available.
     */
    updateBlock(pageKey, blockId, propPatch) {
      try {
        let cfg = this.cfg;
        for (const [key, value] of Object.entries(propPatch)) {
          cfg = typeof updateBlockProp === 'function'
            ? updateBlockProp(cfg, blockId, key, value)
            : (() => {
                const blk = (cfg.pages[pageKey]?.blocks || []).find(b => b.id === blockId);
                if (blk) blk.props[key] = value;
                return cfg;
              })();
          Logger.log('STATE_UPDATE', { type: 'block_prop', blockId, key, value });
        }
        this.cfg = cfg;
        this._commit();
      } catch (e) {
        Logger.log('BLOCK_ERROR', { blockId, error: e.message });
        this._toast('Block update failed: ' + e.message, 'error');
      }
    },

    /**
     * updateBlockStyles(pageKey, blockId, stylesPatch) — safe block style update.
     */
    updateBlockStyles(pageKey, blockId, stylesPatch) {
      try {
        let cfg = this.cfg;
        for (const [key, value] of Object.entries(stylesPatch)) {
          cfg = typeof updateBlockStyle === 'function'
            ? updateBlockStyle(cfg, blockId, key, value)
            : (() => {
                const blk = (cfg.pages[pageKey]?.blocks || []).find(b => b.id === blockId);
                if (blk) blk.styles[key] = value;
                return cfg;
              })();
          Logger.log('STATE_UPDATE', { type: 'block_style', blockId, key, value });
        }
        this.cfg = cfg;
        this._commit();
      } catch (e) {
        Logger.log('BLOCK_ERROR', { blockId, error: e.message });
        this._toast('Style update failed: ' + e.message, 'error');
      }
    },

    // ── 4d. History (undo / redo) ─────────────────────────────────────────────

    _pushHistory() {
      // Truncate any redo branch
      this._history = this._history.slice(0, this._historyIdx + 1);
      this._history.push(clone(this.cfg));
      this._historyIdx = this._history.length - 1;
      // Cap at 60 entries to avoid memory growth
      if (this._history.length > 60) {
        this._history.shift();
        this._historyIdx--;
      }
    },

    undo() {
      if (!this.canUndo) return;
      this._historyIdx--;
      this.cfg = clone(this._history[this._historyIdx]);
      this._afterHistoryRestore();
    },

    redo() {
      if (!this.canRedo) return;
      this._historyIdx++;
      this.cfg = clone(this._history[this._historyIdx]);
      this._afterHistoryRestore();
    },

    _afterHistoryRestore() {
      this._syncSectionPage();
      _applyTheme(this.cfg, null);
      this.debouncedPreview();
    },

    // ── 4e. Project system ────────────────────────────────────────────────────

    async loadProjects() {
      const { ok, data } = await API.listProjects();
      if (ok) this.projects = data;
    },

    async createProject() {
      const name = prompt('Project name:', 'My Website');
      if (!name?.trim()) return;
      this.saving = true;
      const { ok, data, error } = await API.createProject(name.trim(), this.cfg);
      if (ok && data.ok) {
        this.currentProject = { id: data.id, name: data.name };
        this.projectId      = data.id;
        this._lastSavedHash = cfgHash(this.cfg);
        await this.loadProjects();
        this.activeTab = 'Setup';
        this._toast(`"${data.name}" created ✓`);
      } else {
        this._toast(error || 'Create failed', 'error');
      }
      this.saving = false;
    },

    async loadProject(pid) {
      const { ok, data, error } = await API.getProject(pid);
      if (!ok) { this._toast(error || 'Load failed', 'error'); return; }
      if (data.error) { this._toast('Project not found', 'error'); return; }

      // Full schema validation on load
      Logger.log('API_CALL', { action: 'loadProject', pid });
      if (typeof BLOCK_CONTRACTS !== 'undefined') {
        const result = validateConfig(data.config);
        this.cfg = result.config;
        if (result.errors?.length) {
          Logger.log('CONFIG_ERROR', { source: 'loadProject', errors: result.errors });
          this._toast(`Config repaired (${result.errors.length} issue${result.errors.length > 1 ? 's' : ''})`, 'warning');
        }
      } else {
        this.cfg = typeof validateConfig === 'function' ? validateConfig(data.config) : data.config;
      }

      this.currentProject  = { id: data.id, name: data.name, publish_url: data.publish_url };
      this.projectId       = data.id;
      this._lastSavedHash  = cfgHash(this.cfg);
      this._lastPreviewKey = '';

      this._pushHistory();
      this._syncSectionPage();
      _applyTheme(this.cfg, null);
      this._buildPreview();
      this.activeTab = 'Setup';
      await this.loadPublishVersions();
      this._toast(`Loaded "${data.name}" ✓`);
    },

    async saveProject() {
      this._persistLocal();
      this.saving = true;
      if (this.currentProject) {
        const { ok, error } = await API.updateProject(this.projectId, { config: this.cfg, name: this.currentProject.name });
        if (ok) {
          this._lastSavedHash = cfgHash(this.cfg);
          await this.loadProjects();
          this._toast('Saved ✓');
        } else {
          this._toast(error || 'Save failed', 'error');
        }
      } else {
        // No project yet — save to legacy config.json
        const { ok, error } = await API.saveConfig(this.cfg);
        this._toast(ok ? 'Saved locally ✓' : (error || 'Save failed'), ok ? 'info' : 'error');
      }
      this.saving = false;
    },

    async deleteProject(pid) {
      const p = this.projects.find(x => x.id === pid);
      if (!confirm(`Delete "${p?.name || pid}"? This cannot be undone.`)) return;
      const { ok, error } = await API.deleteProject(pid);
      if (ok) {
        if (this.currentProject?.id === pid) { this.currentProject = null; this.projectId = 'default'; }
        await this.loadProjects();
        this._toast('Project deleted');
      } else {
        this._toast(error || 'Delete failed', 'error');
      }
    },

    async duplicateProject(pid) {
      const { ok, data, error } = await API.duplicateProject(pid);
      if (ok && data.ok) {
        await this.loadProjects();
        this._toast(`Duplicated as "${data.name}" ✓`);
      } else {
        this._toast(error || 'Duplicate failed', 'error');
      }
    },

    async publishProject() {
      if (!this.currentProject) { this._toast('Create a project first', 'warning'); return; }
      this.publishing = true;
      // Save latest config before publishing
      await API.updateProject(this.projectId, { config: this.cfg, name: this.currentProject.name });
      const { ok, data, error } = await API.publish(this.projectId);
      if (!ok) { this._toast(error || 'Publish failed', 'error'); this.publishing = false; return; }

      // Poll background job until done
      const jid = data.job_id;
      if (jid) {
        this._toast('Building site…', 'info');
        const poll = async () => {
          const { ok: jok, data: jdata } = await API.publishStatus(jid);
          if (!jok || jdata.status === 'error') {
            this._toast('Publish failed: ' + (jdata?.error || 'unknown'), 'error');
            this.publishing = false;
            return;
          }
          if (jdata.status === 'done') {
            const result = jdata.result || {};
            this.publishUrl = window.location.origin + (result.url || '');
            if (this.currentProject) this.currentProject.publish_url = result.url;
            await this.loadProjects();
            await this.loadPublishVersions();
            this._toast('Site published ✓', 'success');
            this.publishing = false;
          } else {
            setTimeout(poll, 800);
          }
        };
        setTimeout(poll, 600);
      } else {
        this.publishing = false;
      }
    },

    async loadPublishVersions() {
      if (!this.currentProject) return;
      const { ok, data } = await API.listVersions(this.projectId);
      if (ok) this.publishVersions = data;
    },

    async rollbackVersion(ver) {
      if (!confirm(`Restore version ${ver}? This replaces the current live site.`)) return;
      const { ok, data, error } = await API.rollback(this.projectId, ver);
      if (ok && data.ok) {
        this._toast(`Rolled back to ${ver} ✓`);
        await this.loadPublishVersions();
      } else {
        this._toast(error || 'Rollback failed', 'error');
      }
    },

    async cleanupUploads() {
      if (!this.currentProject) return;
      const { ok, data, error } = await API.cleanupUploads(this.projectId);
      if (ok && data.ok) {
        const n = data.removed?.length || 0;
        this._toast(n > 0 ? `Removed ${n} unused file${n > 1 ? 's' : ''}` : 'No unused files', 'info');
      } else {
        this._toast(error || 'Cleanup failed', 'error');
      }
    },

    /** Autosave — only fires if config has changed since last save. */
    async _autoSave() {
      if (!this.currentProject) return;
      const h = cfgHash(this.cfg);
      if (h === this._lastSavedHash) return;
      this.autoSaving = true;
      const { ok, data } = await API.updateProject(this.projectId, { config: this.cfg, name: this.currentProject.name });
      if (ok && data.ok && !data.skipped) this._lastSavedHash = h;
      this.autoSaving = false;
    },

    // ── 4f. Preview ───────────────────────────────────────────────────────────

    triggerPreview() { this.debouncedPreview(); },

    switchPreviewPage(pageKey) {
      this.previewPage     = pageKey;
      this._lastPreviewKey = '';   // force rebuild
      this._buildPreview();
    },

    async _buildPreview() {
      // Compute a stable key — skip if nothing changed
      const activeCfg = this._activeCfg();
      const key = `${cfgHash(activeCfg)}:${this.previewPage}:${this.previewMode}`;
      if (key === this._lastPreviewKey) return;
      this._lastPreviewKey = key;
      this.previewing  = true;
      this.buildError  = '';

      if (this.previewMode === 'url') {
        await this._buildPreviewUrl(activeCfg);
      } else {
        await this._buildPreviewSrcdoc(activeCfg);
      }
      this.previewing = false;
    },

    async _buildPreviewSrcdoc(activeCfg) {
      Logger.log('API_CALL', { action: 'preview', page: this.previewPage });
      const t0 = performance.now();
      const { ok, data, error } = await API.preview(activeCfg, this.previewPage, true);
      const elapsed = Math.round(performance.now() - t0);

      if (!ok) {
        this.buildError = error || 'Build failed';
        Logger.log('PREVIEW_BUILD', { page: this.previewPage, ms: elapsed, ok: false, error: this.buildError });
        const frame = document.getElementById('previewFrame');
        if (frame) frame.srcdoc = this._offlinePage(this.buildError);
        return;
      }
      if (!data.ok) {
        this.buildError = data.error || 'Build failed';
        Logger.log('PREVIEW_BUILD', { page: this.previewPage, ms: elapsed, ok: false, error: this.buildError });
        return;
      }

      this.buildMs      = data.build_ms || elapsed;
      this.devLastBuild = this.buildMs;
      this.buildError   = '';
      Logger.log('PREVIEW_BUILD', { page: this.previewPage, ms: this.buildMs, cached: !!data.cached });

      const frame = document.getElementById('previewFrame');
      if (!frame) return;
      frame.srcdoc = data.html;
      frame.onload = () => _applyTheme(this.cfg, frame);
    },

    async _buildPreviewUrl(activeCfg) {
      const { ok, data, error } = await API.previewUrl(activeCfg, this.projectId);
      if (!ok) { this._toast(error || 'URL preview failed', 'error'); return; }
      const url   = (data.pages || {})[this.previewPage] || (data.base + 'index.html');
      const frame = document.getElementById('previewFrame');
      if (!frame) return;
      frame.src    = url;
      frame.onload = () => _applyTheme(this.cfg, frame);
      this.previewUrl = url;
    },

    _offlinePage(msg = 'Server offline') {
      return `<!DOCTYPE html><html><body style="font-family:system-ui;padding:2rem;background:#0f0f1a;color:#e2e8f0">
<div style="max-width:480px;margin:5rem auto;text-align:center">
  <div style="font-size:3rem;margin-bottom:1rem">🔌</div>
  <h2 style="color:#bb86fc;margin-bottom:.5rem">${msg}</h2>
  <p style="color:#888;font-size:.9rem;margin-bottom:1.5rem">Start the backend:</p>
  <code style="background:#1a1a2e;color:#03dac6;padding:.75rem 1.25rem;border-radius:.5rem;display:block;font-size:.85rem">
    cd static-site/builder/ui<br>python server.py
  </code>
</div></body></html>`;
    },

    // ── 4g. iframe bridge handler ─────────────────────────────────────────────

    _onFrameMessage(e) {
      const d = e.data;
      if (!d || typeof d.type !== 'string') return;

      switch (d.type) {
        case MSG.SELECT:
          this.selectedSection     = d.id   || null;
          this.selectedSectionName = d.name || d.id || '';
          this._focusTabForSection(this.selectedSectionName);
          break;

        case MSG.DESELECT:
          this.selectedSection     = null;
          this.selectedSectionName = '';
          break;

        case MSG.ACTION:
          this._handleBridgeAction(d.action, d.id);
          break;

        case MSG.TEXT_EDIT:
          // Sanitize before touching config
          this._syncInlineTextEdit({ ...d, text: stripTags(d.text) });
          break;

        case MSG.IMAGE_CLICK:
          this.uploadTarget    = { section: d.sec, src: d.src };
          this.showImageUpload = true;
          break;
      }
    },

    /** Map a section name to the correct editor tab. */
    _focusTabForSection(name) {
      const TAB_MAP = {
        hero:'Setup', about_story:'Setup', contact:'Setup', cta:'Setup',
        stats:'Content', features:'Content', testimonials:'Content',
        services:'Content', team:'Content', pricing:'Content',
        faq:'Content', blog:'Content', portfolio:'Content',
      };
      const CONTENT_MAP = {
        features:'Features', testimonials:'Testimonials', team:'Team',
        pricing:'Pricing', stats:'Stats', faq:'FAQ',
      };
      const tab = TAB_MAP[name] || 'Content';
      this.activeTab = tab;
      if (tab === 'Content' && CONTENT_MAP[name]) this.contentTab = CONTENT_MAP[name];
    },

    /** Handle toolbar actions sent from the bridge (dup / hide / del). */
    _handleBridgeAction(action, sectionId) {
      // Match by prefix — bridge IDs are like "section_1"
      const idx = this.currentSections.findIndex(s => sectionId.startsWith(s));
      if (idx === -1) return;
      if (action === 'dup')  this.duplicateSection(idx);
      if (action === 'hide') this.toggleSectionVisibility(this.currentSections[idx]);
      if (action === 'del')  this.removeSection(idx);
    },

    /** Best-effort sync of inline text edits back to config. */
    _syncInlineTextEdit(d) {
      if (!d.text) return;
      const t = d.text.trim();
      // Only sync known safe fields — avoids corrupting structured content
      if (d.tag === 'P' && d.sec?.includes('hero')) this.cfg.description = t;
      this._commit();
    },

    /** Send a highlight message to the iframe. */
    highlightSection(name) {
      const frame = document.getElementById('previewFrame');
      if (!frame) return;
      try { frame.contentWindow.postMessage({ type: MSG.HIGHLIGHT, id: name }, '*'); } catch (_) {}
    },

    // ── 4h. Sections ──────────────────────────────────────────────────────────

    /** Sync currentSections from cfg.pages[sectionPage]. */
    _syncSectionPage() {
      const page = this.cfg?.pages?.[this.sectionPage];
      this.currentSections = page ? clone(page.sections || []) : [];
    },

    /** Write currentSections back to cfg. */
    _flushSections() {
      const page = this.cfg?.pages?.[this.sectionPage];
      if (page) page.sections = clone(this.currentSections);
    },

    addSection(name) {
      if (this.currentSections.includes(name)) return;
      this.currentSections.push(name);
      this._flushSections();
      this._commit();
    },

    removeSection(idx) {
      if (!confirm(`Remove "${this.currentSections[idx]}" section?`)) return;
      this.currentSections.splice(idx, 1);
      this._flushSections();
      this._commit();
    },

    duplicateSection(idx) {
      this.currentSections.splice(idx + 1, 0, this.currentSections[idx]);
      this._flushSections();
      this._commit();
      this._toast('Section duplicated');
    },

    toggleSectionVisibility(name) {
      const p = this.sectionPage;
      if (!this.hiddenSections[p]) this.hiddenSections[p] = new Set();
      const set = this.hiddenSections[p];
      set.has(name) ? set.delete(name) : set.add(name);
      this._commit();
    },

    isSectionHidden(name) {
      return !!(this.hiddenSections[this.sectionPage]?.has(name));
    },

    // Drag-and-drop reorder
    dragStart(idx)  { this._dragIdx = idx; },
    dragEnd()       { this._dragIdx = null; },
    dragDrop()      { this._flushSections(); this._commit(); },
    dragOver(idx) {
      if (this._dragIdx === null || this._dragIdx === idx) return;
      const item = this.currentSections.splice(this._dragIdx, 1)[0];
      this.currentSections.splice(idx, 0, item);
      this._dragIdx = idx;
    },

    // ── 4i. Blocks ────────────────────────────────────────────────────────────

    get filteredBlocks() {
      if (this.blockFilter === 'All') return this.allBlocks;
      return this.allBlocks.filter(b => b.category === this.blockFilter);
    },

    insertBlock(type) {
      if (typeof createBlock !== 'function') { this._toast('Block library not loaded', 'error'); return; }
      let blk = createBlock(type);
      if (!blk) return;
      // Sanitize through schema contract before inserting
      if (typeof sanitizeBlock === 'function') {
        blk = sanitizeBlock(blk);
        const { valid, errors } = typeof validateBlock === 'function' ? validateBlock(blk) : { valid: true, errors: [] };
        if (!valid) {
          Logger.log('BLOCK_ERROR', { type, errors });
          // Still insert — sanitizeBlock already fixed what it could
        }
      }
      const page = this.cfg.pages[this.sectionPage];
      if (!page) return;
      if (!Array.isArray(page.blocks)) page.blocks = [];
      page.blocks.push(blk);
      this.showBlockLibrary = false;
      Logger.log('STATE_UPDATE', { action: 'insertBlock', type, id: blk.id });
      this._commit();
      this._toast(`"${type}" block added ✓`);
    },

    removeBlock(pageKey, idx) {
      if (!confirm('Remove this block?')) return;
      const page = this.cfg.pages[pageKey];
      if (page?.blocks) { page.blocks.splice(idx, 1); this._commit(); }
    },

    duplicateBlock(pageKey, idx) {
      const page = this.cfg.pages[pageKey];
      if (!page?.blocks) return;
      const copy = clone(page.blocks[idx]);
      copy.id = typeof makeBlockId === 'function' ? makeBlockId() : 'blk_' + Date.now().toString(36);
      page.blocks.splice(idx + 1, 0, copy);
      this._commit();
      this._toast('Block duplicated');
    },

    // ── 4j. Style editor ──────────────────────────────────────────────────────

    openStyleEditor(blockId) {
      this.selectedBlockId = blockId;
      // Load existing styles into selStyles
      for (const page of Object.values(this.cfg.pages)) {
        const blk = (page.blocks || []).find(b => b.id === blockId);
        if (blk) { Object.assign(this.selStyles, blk.styles || {}); break; }
      }
      this.showStyleEditor = true;
    },

    applyStyleEdit() {
      if (!this.selectedBlockId) return;
      try {
        // Use schema-safe updateBlockStyle for each changed style key
        let cfg = this.cfg;
        for (const [key, value] of Object.entries(this.selStyles)) {
          cfg = typeof updateBlockStyle === 'function'
            ? updateBlockStyle(cfg, this.selectedBlockId, key, value)
            : (() => {
                for (const page of Object.values(cfg.pages)) {
                  const blk = (page.blocks || []).find(b => b.id === this.selectedBlockId);
                  if (blk) { blk.styles[key] = value; break; }
                }
                return cfg;
              })();
        }
        this.cfg = cfg;
        Logger.log('STATE_UPDATE', { action: 'applyStyleEdit', blockId: this.selectedBlockId });

        // Push live CSS to iframe without a full rebuild
        const frame = document.getElementById('previewFrame');
        if (frame) {
          try {
            frame.contentWindow.postMessage({
              type:    MSG.STYLE_UPDATE,
              blockId: this.selectedBlockId,
              css:     this._stylesToCss(this.selStyles),
            }, '*');
          } catch (_) {}
        }
        this._commit();
      } catch (e) {
        Logger.log('BLOCK_ERROR', { blockId: this.selectedBlockId, error: e.message });
        this._toast('Style update failed: ' + e.message, 'error');
      }
    },

    _stylesToCss(s) {
      const bg = s.bgType === 'transparent' ? 'transparent'
               : s.bgType === 'gradient'    ? `linear-gradient(135deg,${this.cfg.primary_color},${this.cfg.secondary_color})`
               : (s.bgColor || '#fff');
      return [
        `font-size:${s.fontSize}`,
        `font-weight:${s.fontWeight}`,
        `line-height:${s.lineHeight}`,
        `text-align:${s.textAlign}`,
        `color:${s.textColor}`,
        `background:${bg}`,
        `padding:${s.paddingTop} ${s.paddingRight} ${s.paddingBottom} ${s.paddingLeft}`,
        `margin:${s.marginTop} 0 ${s.marginBottom}`,
        `border:${s.borderWidth} solid ${s.borderColor}`,
        `border-radius:${s.borderRadius}`,
        `box-shadow:${s.shadow}`,
      ].join(';');
    },

    // ── 4k. Theme ─────────────────────────────────────────────────────────────

    onThemeChange() {
      const frame = document.getElementById('previewFrame');
      _applyTheme(this.cfg, frame);
      this._commit();
    },

    applyTemplate(tpl) {
      this.cfg.primary_color   = tpl.primary;
      this.cfg.secondary_color = tpl.secondary;
      this.cfg.site_name       = tpl.site_name;
      this.cfg.tagline         = tpl.tagline;
      this.showTemplates       = false;
      _applyTheme(this.cfg, null);
      this._commit();
      this._toast(`Template "${tpl.name}" applied ✓`);
    },

    applyThemePreset(preset) {
      this.cfg.primary_color   = preset.primary;
      this.cfg.secondary_color = preset.secondary;
      _applyTheme(this.cfg, null);
      this._commit();
      this._toast(`Theme "${preset.name}" applied ✓`);
    },

    // ── 4l. Page manager ──────────────────────────────────────────────────────

    togglePage(key) {
      const i = this.disabledPages.indexOf(key);
      if (i >= 0) this.disabledPages.splice(i, 1);
      else        this.disabledPages.push(key);
      this._commit();
    },

    addPage() {
      const title = prompt('Page title:', 'New Page');
      if (!title?.trim()) return;
      const slug = title.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || ('page_' + Date.now());
      if (this.cfg.pages[slug]) { this._toast('A page with that slug already exists', 'error'); return; }
      this.cfg.pages[slug] = { title: title.trim(), file: slug + '.html', slug: '/' + slug, sections: [], blocks: [] };
      this._commit();
      this._toast(`Page "${title.trim()}" created ✓`);
    },

    renamePage(key) {
      const title = prompt('New title:', this.cfg.pages[key]?.title || key);
      if (!title?.trim()) return;
      this.cfg.pages[key].title = title.trim();
      this._commit();
    },

    deletePage(key) {
      if (Object.keys(this.cfg.pages).length <= 1) { this._toast('Cannot delete the last page', 'error'); return; }
      if (!confirm(`Delete page "${this.cfg.pages[key]?.title || key}"?`)) return;
      delete this.cfg.pages[key];
      if (this.previewPage  === key) this.previewPage  = Object.keys(this.cfg.pages)[0];
      if (this.sectionPage  === key) this.sectionPage  = Object.keys(this.cfg.pages)[0];
      this._syncSectionPage();
      this._commit();
    },

    // ── 4m. Content items ─────────────────────────────────────────────────────

    addItem(key, tpl) {
      if (!Array.isArray(this.cfg.content[key])) this.cfg.content[key] = [];
      this.cfg.content[key].push(clone(tpl));
      this._commit();
    },

    removeItem(key, idx) {
      if (!confirm('Remove this item?')) return;
      this.cfg.content[key].splice(idx, 1);
      this._commit();
    },

    // ── 4n. Upload / media ────────────────────────────────────────────────────

    async uploadImage(event) {
      const file = event.target.files?.[0];
      if (!file) return;
      this.uploading = true;
      const { ok, data, error } = await API.upload(file, this.projectId);
      if (ok && data.ok) {
        this.uploadedImages.unshift({ url: data.url, filename: data.filename });
        this._toast('Image uploaded ✓');
        if (this.uploadTarget) this._applyUploadedImage(data.url);
      } else {
        this._toast(error || data?.error || 'Upload failed', 'error');
      }
      this.uploading = false;
    },

    _applyUploadedImage(url) {
      const frame = document.getElementById('previewFrame');
      if (frame && this.uploadTarget) {
        try {
          frame.contentWindow.postMessage({ type: MSG.REPLACE_IMAGE, oldSrc: this.uploadTarget.src, newSrc: url }, '*');
        } catch (_) {}
      }
      this.uploadTarget    = null;
      this.showImageUpload = false;
      this._commit();
    },

    selectUploadedImage(url) { this._applyUploadedImage(url); },

    // ── 4o. Export ────────────────────────────────────────────────────────────

    async exportSite() {
      if (this.exporting) return;
      this.exporting = true;
      const { ok, data, error } = await API.exportZip(this._activeCfg(), this.exportMode);
      if (ok) {
        const url = URL.createObjectURL(data);
        const a   = document.createElement('a');
        a.href     = url;
        a.download = (this.cfg.site_name || 'website').toLowerCase().replace(/\s+/g, '_') + '.zip';
        a.click();
        URL.revokeObjectURL(url);
        this._toast(`Downloaded as ${this.exportMode} ✓`);
      } else {
        this._toast(error || 'Export failed', 'error');
      }
      this.exporting = false;
    },

    copyJson() {
      navigator.clipboard
        .writeText(JSON.stringify(this._activeCfg(), null, 2))
        .then(() => this._toast('Config copied ✓'))
        .catch(() => this._toast('Copy failed', 'error'));
    },

    // ── 4p. Private helpers ───────────────────────────────────────────────────

    /**
     * _commit() — the single place that records history, persists locally,
     * and schedules a preview rebuild + autosave.
     * All mutations must call this exactly once at the end.
     */
    _commit() {
      this._pushHistory();
      this._persistLocal();
      this.debouncedPreview();
      this.debouncedAutoSave();
      // Emit snapshot event for collaboration/diagnostics
      if (typeof Events !== 'undefined') {
        Events.snapshot(this.cfg);
      }
      // Refresh dev panel logs if open
      if (this.debugMode && typeof Logger !== 'undefined') {
        this.devLogs = Logger.getLogs(30);
      }
      if (this.debugMode && typeof DevTools !== 'undefined') {
        this.devReport = DevTools.getReport(this.cfg);
      }
    },

    /**
     * _activeCfg() — returns a copy of cfg with disabled pages and hidden
     * sections removed. Used for preview and export — never mutates this.cfg.
     */
    _activeCfg() {
      const c = clone(this.cfg);
      // Remove disabled pages
      for (const k of this.disabledPages) delete c.pages[k];
      // Remove hidden sections per page
      for (const [pk, hidden] of Object.entries(this.hiddenSections)) {
        if (c.pages[pk] && hidden.size > 0) {
          c.pages[pk].sections = (c.pages[pk].sections || []).filter(s => !hidden.has(s));
        }
      }
      return c;
    },

    /** Persist state to localStorage. */
    _persistLocal() {
      try {
        localStorage.setItem('wbs_cfg',      JSON.stringify(this.cfg));
        localStorage.setItem('wbs_disabled', JSON.stringify(this.disabledPages));
        localStorage.setItem('wbs_images',   JSON.stringify(this.uploadedImages));
        // Serialise Sets to arrays
        const h = Object.fromEntries(
          Object.entries(this.hiddenSections).map(([k, v]) => [k, [...v]])
        );
        localStorage.setItem('wbs_hidden', JSON.stringify(h));
      } catch (_) {}
    },

    /**
     * _loadLocal() — read from localStorage and return raw config (or null).
     * Also restores disabledPages, hiddenSections, uploadedImages.
     */
    _loadLocal() {
      try {
        const d = localStorage.getItem('wbs_disabled');
        if (d) this.disabledPages = JSON.parse(d);

        const h = localStorage.getItem('wbs_hidden');
        if (h) {
          const r = JSON.parse(h);
          this.hiddenSections = Object.fromEntries(
            Object.entries(r).map(([k, v]) => [k, new Set(v)])
          );
        }

        const i = localStorage.getItem('wbs_images');
        if (i) this.uploadedImages = JSON.parse(i);

        const c = localStorage.getItem('wbs_cfg');
        return c ? JSON.parse(c) : null;
      } catch (_) {
        return null;
      }
    },

    /** Show a toast. Cancels any previous one first. */
    _toast(msg, type = 'success') {
      if (this._rmToast) this._rmToast();
      this._rmToast = createToast(msg, type);
    },

  })); // end Alpine.data
}); // end alpine:init
