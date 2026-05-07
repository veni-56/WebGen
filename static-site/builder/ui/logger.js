/**
 * logger.js — Structured debug logger for the Website Builder.
 *
 * Usage:
 *   Logger.log('STATE_UPDATE', { path: 'site_name', value: 'Foo' });
 *   Logger.log('API_CALL',     { url: '/api/preview', ms: 120 });
 *   Logger.log('PREVIEW_BUILD',{ page: 'home', ms: 340, cached: false });
 *   Logger.log('BLOCK_ERROR',  { blockId: 'blk_abc', errors: [...] });
 *
 *   Logger.enable();   // turn on (also set via debugMode in Alpine)
 *   Logger.disable();  // turn off
 *   Logger.getLogs();  // returns array of recent log entries
 *   Logger.clear();    // clear log buffer
 */
'use strict';

const Logger = (() => {
  const MAX_ENTRIES = 200;
  let   _enabled    = false;
  const _buffer     = [];   // circular log buffer

  // ANSI-style console colors via CSS (Chrome DevTools supports this)
  const COLORS = {
    STATE_UPDATE:  '#8b5cf6',
    API_CALL:      '#0ea5e9',
    PREVIEW_BUILD: '#10b981',
    BLOCK_ERROR:   '#ef4444',
    CONFIG_ERROR:  '#f59e0b',
    SCHEMA_FIX:    '#f97316',
    PERF:          '#6366f1',
    INFO:          '#64748b',
  };

  function _entry(tag, data) {
    return {
      tag,
      data,
      ts:    Date.now(),
      time:  new Date().toISOString().slice(11, 23), // HH:MM:SS.mmm
    };
  }

  return {
    enable()  { _enabled = true;  },
    disable() { _enabled = false; },
    isEnabled() { return _enabled; },

    /**
     * log(tag, data) — record a log entry.
     * tag: one of the COLORS keys above, or any string.
     * data: any JSON-serialisable value.
     */
    log(tag, data) {
      const entry = _entry(tag, data);

      // Always push to buffer (even when disabled) so dev panel can show history
      _buffer.push(entry);
      if (_buffer.length > MAX_ENTRIES) _buffer.shift();

      if (!_enabled) return;

      const color = COLORS[tag] || '#64748b';
      const label = `%c[WBS:${tag}]`;
      const style = `color:${color};font-weight:700;font-size:.75rem`;

      if (typeof data === 'object' && data !== null) {
        console.groupCollapsed(label, style, entry.time);
        console.log(data);
        console.groupEnd();
      } else {
        console.log(label, style, entry.time, data);
      }
    },

    /** Return a copy of the log buffer (most recent first). */
    getLogs(limit = 50) {
      return _buffer.slice(-limit).reverse();
    },

    /** Return only entries matching a tag. */
    getByTag(tag, limit = 20) {
      return _buffer.filter(e => e.tag === tag).slice(-limit).reverse();
    },

    /** Clear the buffer. */
    clear() { _buffer.length = 0; },

    /** Measure and log execution time of an async function. */
    async time(tag, label, fn) {
      const t0 = performance.now();
      let result;
      try {
        result = await fn();
      } finally {
        const ms = Math.round(performance.now() - t0);
        this.log(tag, { label, ms });
      }
      return result;
    },
  };
})();
