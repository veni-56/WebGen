/**
 * diagnostics/dev_tools.js — Developer diagnostics panel.
 * Only active when debugMode === true in the Alpine component.
 *
 * Provides:
 *   DevTools.renderProfiler   — timing per block render
 *   DevTools.blockTree        — current block tree snapshot
 *   DevTools.stateDiff        — diff between two config snapshots
 *   DevTools.pluginInspector  — plugin state
 *   DevTools.eventTimeline    — recent events
 *   DevTools.getReport()      — full diagnostic report
 */
'use strict';

const DevTools = (() => {
  const _profile = [];   // [{ blockId, type, ms, ts }]
  const MAX_PROFILE = 200;

  // ── Render profiler ───────────────────────────────────────────────────────
  const renderProfiler = {
    record(blockId, type, ms) {
      _profile.push({ blockId, type, ms, ts: Date.now() });
      if (_profile.length > MAX_PROFILE) _profile.shift();
    },
    getSlowest(n = 10) {
      return [..._profile].sort((a, b) => b.ms - a.ms).slice(0, n);
    },
    getAvgByType() {
      const acc = {};
      for (const e of _profile) {
        if (!acc[e.type]) acc[e.type] = { total: 0, count: 0 };
        acc[e.type].total += e.ms;
        acc[e.type].count++;
      }
      return Object.fromEntries(
        Object.entries(acc).map(([t, v]) => [t, { avg: Math.round(v.total / v.count), count: v.count }])
      );
    },
    clear() { _profile.length = 0; },
  };

  // ── Block tree inspector ──────────────────────────────────────────────────
  const blockTree = {
    snapshot(cfg) {
      const tree = {};
      for (const [pageKey, page] of Object.entries(cfg?.pages || {})) {
        tree[pageKey] = {
          sections: page.sections || [],
          blocks:   (page.blocks || []).map(b => ({
            id:    b.id,
            type:  b.type,
            props: Object.keys(b.props || {}),
          })),
        };
      }
      return tree;
    },
  };

  // ── State diff ────────────────────────────────────────────────────────────
  const stateDiff = {
    diff(before, after) {
      const changes = [];
      _diffObj(before, after, '', changes);
      return changes;
    },
  };

  function _diffObj(a, b, path, out) {
    if (typeof a !== typeof b) {
      out.push({ path, from: a, to: b }); return;
    }
    if (typeof a !== 'object' || a === null) {
      if (a !== b) out.push({ path, from: a, to: b });
      return;
    }
    const keys = new Set([...Object.keys(a || {}), ...Object.keys(b || {})]);
    for (const k of keys) {
      _diffObj(a?.[k], b?.[k], path ? `${path}.${k}` : k, out);
    }
  }

  // ── Plugin inspector ──────────────────────────────────────────────────────
  const pluginInspector = {
    getState() {
      if (typeof PluginLoader === 'undefined') return { available: false };
      return {
        available: true,
        plugins:   PluginLoader.getAll(),
        hooks:     typeof Hooks !== 'undefined' ? Hooks.inspect() : {},
      };
    },
  };

  // ── Event timeline ────────────────────────────────────────────────────────
  const eventTimeline = {
    get(limit = 30) {
      if (typeof Events === 'undefined') return [];
      return Events.getLog(null, limit);
    },
  };

  // ── Full report ───────────────────────────────────────────────────────────
  function getReport(cfg) {
    return {
      ts:        new Date().toISOString(),
      renderStats:    typeof getRenderStats === 'function' ? getRenderStats() : {},
      slowestBlocks:  renderProfiler.getSlowest(5),
      avgByType:      renderProfiler.getAvgByType(),
      blockTree:      blockTree.snapshot(cfg),
      plugins:        pluginInspector.getState(),
      recentEvents:   eventTimeline.get(20),
      memory:         typeof performance !== 'undefined' && performance.memory
                        ? { usedMB: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) }
                        : null,
    };
  }

  return { renderProfiler, blockTree, stateDiff, pluginInspector, eventTimeline, getReport };
})();
