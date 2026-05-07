/**
 * core/events.js — Collaboration-ready event pipeline.
 *
 * Events are immutable records of what happened.
 * Hooks are extension points that can modify behaviour.
 * This file handles events.
 *
 * Event types:
 *   block_updated   { blockId, pageKey, prop, value, oldValue }
 *   style_updated   { blockId, pageKey, key, value }
 *   page_created    { pageKey, page }
 *   page_deleted    { pageKey }
 *   section_added   { pageKey, section, idx }
 *   section_deleted { pageKey, idx }
 *   config_changed  { path, value, oldValue }
 *   snapshot        { cfg }   — full state snapshot
 *
 * Architecture note:
 *   Events are stored in an append-only log (in-memory, bounded).
 *   Subscribers receive events in real time.
 *   The log enables state replay and optimistic updates.
 *   WebSocket transport can be added later by replacing _broadcast.
 */
'use strict';

const Events = (() => {
  const MAX_LOG   = 500;
  const _log      = [];                    // append-only event log
  const _subs     = new Map();             // eventType → Set<fn>
  const _allSubs  = new Set();             // subscribers for all events
  let   _seq      = 0;                     // monotonic sequence number

  function _emit(type, payload, sourceId = 'local') {
    const event = {
      seq:       ++_seq,
      type,
      payload,
      sourceId,
      ts:        Date.now(),
    };
    // Append to log (bounded)
    _log.push(event);
    if (_log.length > MAX_LOG) _log.shift();

    // Notify type-specific subscribers
    const typeSubs = _subs.get(type);
    if (typeSubs) typeSubs.forEach(fn => { try { fn(event); } catch(e) {} });

    // Notify wildcard subscribers
    _allSubs.forEach(fn => { try { fn(event); } catch(e) {} });

    return event;
  }

  return {
    // ── Emit ────────────────────────────────────────────────────────────────

    blockUpdated(blockId, pageKey, prop, value, oldValue) {
      return _emit('block_updated', { blockId, pageKey, prop, value, oldValue });
    },
    styleUpdated(blockId, pageKey, key, value) {
      return _emit('style_updated', { blockId, pageKey, key, value });
    },
    pageCreated(pageKey, page) {
      return _emit('page_created', { pageKey, page });
    },
    pageDeleted(pageKey) {
      return _emit('page_deleted', { pageKey });
    },
    sectionAdded(pageKey, section, idx) {
      return _emit('section_added', { pageKey, section, idx });
    },
    sectionDeleted(pageKey, idx) {
      return _emit('section_deleted', { pageKey, idx });
    },
    configChanged(path, value, oldValue) {
      return _emit('config_changed', { path, value, oldValue });
    },
    snapshot(cfg) {
      return _emit('snapshot', { cfg: JSON.parse(JSON.stringify(cfg)) });
    },

    // ── Subscribe ────────────────────────────────────────────────────────────

    /** Subscribe to a specific event type. Returns unsubscribe fn. */
    on(type, fn) {
      if (!_subs.has(type)) _subs.set(type, new Set());
      _subs.get(type).add(fn);
      return () => _subs.get(type)?.delete(fn);
    },

    /** Subscribe to all events. Returns unsubscribe fn. */
    onAny(fn) {
      _allSubs.add(fn);
      return () => _allSubs.delete(fn);
    },

    // ── Log access ───────────────────────────────────────────────────────────

    /** Return recent events, optionally filtered by type. */
    getLog(type = null, limit = 50) {
      const entries = type ? _log.filter(e => e.type === type) : _log;
      return entries.slice(-limit);
    },

    /** Return events since a given sequence number (for sync). */
    since(seq) {
      return _log.filter(e => e.seq > seq);
    },

    /** Current sequence number. */
    get seq() { return _seq; },

    /** Clear log (tests). */
    clear() { _log.length = 0; _seq = 0; },
  };
})();
