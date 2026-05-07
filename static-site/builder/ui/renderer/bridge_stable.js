/**
 * renderer/bridge_stable.js — Stable iframe bridge with:
 *   - MutationObserver recovery (re-tags elements added after initial load)
 *   - Selection persistence across re-renders
 *   - Overlay deduplication guard
 *   - Safe DOM patching (update in place, don't rebuild)
 *
 * This file is injected into preview iframes INSTEAD of the raw BRIDGE
 * string in server.py when visual=true.
 *
 * It replaces the inline BRIDGE script with a more robust version.
 * The MSG constants must match core/hooks.js and server.py.
 */
(function () {
  'use strict';

  // ── Message types (must match MSG in app.js) ──────────────────────────────
  const MSG = {
    SELECT:        'wbs:select',
    DESELECT:      'wbs:deselect',
    ACTION:        'wbs:action',
    TEXT_EDIT:     'wbs:text-edit',
    IMAGE_CLICK:   'wbs:image-click',
    THEME:         'wbs:theme',
    HIGHLIGHT:     'wbs:highlight',
    REPLACE_IMAGE: 'wbs:replace-image',
    STYLE_UPDATE:  'wbs:style-update',
  };

  // ── State ─────────────────────────────────────────────────────────────────
  let _selected    = null;   // currently selected element
  let _selectedId  = null;   // data-wbs id of selected element
  let _observer    = null;   // MutationObserver for recovery

  // ── Styles (injected once) ────────────────────────────────────────────────
  function _injectStyles() {
    if (document.getElementById('wbs-bridge-styles')) return;
    const st = document.createElement('style');
    st.id = 'wbs-bridge-styles';
    st.textContent = `
      [data-wbs]{position:relative;cursor:pointer;transition:outline .12s,box-shadow .12s}
      [data-wbs]:hover{outline:2px dashed rgba(108,99,255,.45);outline-offset:3px}
      [data-wbs].wbs-sel{outline:2.5px solid #6c63ff!important;outline-offset:3px;
        box-shadow:0 0 0 4px rgba(108,99,255,.15)!important}
      .wbs-label{position:absolute;top:-22px;left:0;background:#6c63ff;color:#fff;
        font-size:10px;font-weight:700;padding:2px 7px;border-radius:4px 4px 0 0;
        letter-spacing:.04em;pointer-events:none;z-index:9999;white-space:nowrap}
      .wbs-tb{position:absolute;top:-22px;right:0;display:flex;gap:2px;background:#1e1b4b;
        border-radius:4px;padding:2px 4px;z-index:9999;opacity:0;transition:opacity .15s;
        pointer-events:none}
      [data-wbs]:hover .wbs-tb,[data-wbs].wbs-sel .wbs-tb{opacity:1;pointer-events:auto}
      .wbs-tb button{background:none;border:none;color:#c4b5fd;cursor:pointer;
        font-size:11px;padding:1px 5px;border-radius:3px;line-height:1.4}
      .wbs-tb button:hover{background:rgba(255,255,255,.15);color:#fff}
      [contenteditable]:focus{outline:2px solid #6c63ff;outline-offset:1px;
        border-radius:2px;background:rgba(108,99,255,.04)}
    `;
    document.head.appendChild(st);
  }

  // ── Tag a single element (idempotent) ─────────────────────────────────────
  function _tagElement(el, counts) {
    if (el.dataset.wbs) return;   // already tagged — skip (dedup guard)
    const tag = el.tagName.toLowerCase();
    counts[tag] = (counts[tag] || 0) + 1;
    const sid = el.dataset.sectionId || `${tag}_${counts[tag]}`;
    el.dataset.wbs = sid;
    el.style.position = 'relative';

    // Label
    const lb = document.createElement('div');
    lb.className = 'wbs-label';
    lb.textContent = el.dataset.sectionName || tag + (counts[tag] > 1 ? ' ' + counts[tag] : '');
    el.appendChild(lb);

    // Toolbar
    const tb = document.createElement('div');
    tb.className = 'wbs-tb';
    tb.innerHTML =
      '<button title="Edit" onclick="wbsSel(this.closest(\'[data-wbs]\'))">&#9998;</button>' +
      '<button title="Dup"  onclick="wbsAct(\'dup\',this.closest(\'[data-wbs]\').dataset.wbs)">&#10697;</button>' +
      '<button title="Hide" onclick="wbsAct(\'hide\',this.closest(\'[data-wbs]\').dataset.wbs)">&#128065;</button>' +
      '<button title="Del"  onclick="wbsAct(\'del\',this.closest(\'[data-wbs]\').dataset.wbs)">&#10005;</button>';
    el.appendChild(tb);
  }

  // ── Tag all structural elements ───────────────────────────────────────────
  function _tagAll() {
    const counts = {};
    const TAGS = ['section', 'header', 'footer', 'nav', 'article', 'aside', 'main'];
    TAGS.forEach(tag => {
      document.querySelectorAll(tag).forEach(el => _tagElement(el, counts));
    });
  }

  // ── Restore selection after re-render ─────────────────────────────────────
  function _restoreSelection() {
    if (!_selectedId) return;
    const el = document.querySelector(`[data-wbs="${_selectedId}"]`);
    if (el) {
      el.classList.add('wbs-sel');
      _selected = el;
    } else {
      // Element no longer exists — notify parent
      _selected   = null;
      _selectedId = null;
      parent.postMessage({ type: MSG.DESELECT }, '*');
    }
  }

  // ── MutationObserver: re-tag new elements, restore selection ─────────────
  function _startObserver() {
    if (_observer) _observer.disconnect();
    _observer = new MutationObserver((mutations) => {
      let needsRetag = false;
      for (const m of mutations) {
        for (const node of m.addedNodes) {
          if (node.nodeType === 1) { needsRetag = true; break; }
        }
        if (needsRetag) break;
      }
      if (needsRetag) {
        _tagAll();
        _restoreSelection();
      }
    });
    _observer.observe(document.body, { childList: true, subtree: true });
  }

  // ── Public selection API ──────────────────────────────────────────────────
  window.wbsSel = function (el) {
    if (_selected) _selected.classList.remove('wbs-sel');
    _selected   = el;
    _selectedId = el.dataset.wbs;
    el.classList.add('wbs-sel');
    parent.postMessage({
      type: MSG.SELECT,
      id:   el.dataset.wbs,
      name: el.dataset.sectionName || el.dataset.wbs,
    }, '*');
  };

  window.wbsAct = function (action, id) {
    parent.postMessage({ type: MSG.ACTION, action, id }, '*');
  };

  // ── Click handler ─────────────────────────────────────────────────────────
  document.addEventListener('click', e => {
    const el = e.target.closest('[data-wbs]');
    if (el) {
      e.stopPropagation();
      wbsSel(el);
    } else {
      if (_selected) { _selected.classList.remove('wbs-sel'); _selected = null; _selectedId = null; }
      parent.postMessage({ type: MSG.DESELECT }, '*');
    }
  }, true);

  // ── Double-click inline edit ──────────────────────────────────────────────
  document.addEventListener('dblclick', e => {
    const el = e.target;
    if (!['H1','H2','H3','H4','P','SPAN','A','LI','BUTTON'].includes(el.tagName)) return;
    el.contentEditable = 'true';
    el.focus();
    const range = document.createRange();
    range.selectNodeContents(el);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);

    el.addEventListener('blur', function f() {
      el.contentEditable = 'false';
      el.removeEventListener('blur', f);
      parent.postMessage({
        type: MSG.TEXT_EDIT,
        tag:  el.tagName,
        text: el.innerText,   // innerText only — no HTML injection
        sec:  el.closest('[data-wbs]')?.dataset.wbs,
      }, '*');
    }, { once: true });

    el.addEventListener('keydown', function k(ev) {
      if (ev.key === 'Enter')  { ev.preventDefault(); el.blur(); }
      if (ev.key === 'Escape') { el.contentEditable = 'false'; el.removeEventListener('keydown', k); }
    });
  });

  // ── Alt+click image ───────────────────────────────────────────────────────
  document.addEventListener('click', e => {
    if (e.target.tagName === 'IMG' && e.altKey) {
      e.preventDefault();
      parent.postMessage({
        type: MSG.IMAGE_CLICK,
        src:  e.target.src,
        sec:  e.target.closest('[data-wbs]')?.dataset.wbs,
      }, '*');
    }
  });

  // ── Messages from parent ──────────────────────────────────────────────────
  window.addEventListener('message', e => {
    const d = e.data;
    if (!d?.type) return;

    if (d.type === MSG.THEME) {
      let s = document.getElementById('wbs-lt');
      if (!s) { s = document.createElement('style'); s.id = 'wbs-lt'; document.head.appendChild(s); }
      s.textContent = d.css;
    }

    if (d.type === MSG.HIGHLIGHT) {
      document.querySelectorAll('[data-wbs]').forEach(x => x.classList.remove('wbs-sel'));
      const t = document.querySelector(`[data-wbs="${d.id}"]`);
      if (t) { t.classList.add('wbs-sel'); t.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
    }

    if (d.type === MSG.REPLACE_IMAGE) {
      document.querySelectorAll('img').forEach(img => {
        if (img.src === d.oldSrc || img.src.endsWith(d.oldSrc)) img.src = d.newSrc;
      });
    }

    if (d.type === MSG.STYLE_UPDATE && d.blockId) {
      const el = document.querySelector(`[data-block="${d.blockId}"]`) ||
                 document.querySelector(`[data-wbs="${d.blockId}"]`);
      if (el && d.css) {
        // Safe patch: append to existing style, don't replace
        const existing = el.getAttribute('style') || '';
        el.setAttribute('style', existing + ';' + d.css);
      }
    }
  });

  // ── Init ──────────────────────────────────────────────────────────────────
  function _init() {
    _injectStyles();
    _tagAll();
    _startObserver();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _init);
  } else {
    _init();
  }
})();
