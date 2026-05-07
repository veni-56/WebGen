/**
 * editor.js — Style Editor Panel + Rich Text Toolbar
 * Provides Alpine.js data for the right-side style panel.
 * Handles: typography, colors, spacing, border, shadow.
 * Also provides the floating rich-text toolbar for inline editing.
 */
'use strict';

// ── Style panel Alpine component ──────────────────────────────────────────────

function styleEditorData() {
  return {
    // Currently selected block's styles (bound two-way)
    styles: {
      // Typography
      fontSize:   '1rem',
      fontWeight: '400',
      lineHeight: '1.6',
      textAlign:  'left',
      textColor:  '#111827',
      // Background
      bgColor:    '#ffffff',
      bgType:     'solid',   // solid | gradient | transparent
      // Spacing
      paddingTop:    '4rem',
      paddingBottom: '4rem',
      paddingLeft:   '2rem',
      paddingRight:  '2rem',
      marginTop:    '0',
      marginBottom: '0',
      // Border
      borderWidth:  '0',
      borderColor:  '#e5e7eb',
      borderRadius: '0',
      // Shadow
      shadow: 'none',   // none | sm | md | lg | xl
    },

    shadowOptions: [
      { value: 'none',                                                    label: 'None' },
      { value: '0 1px 3px rgba(0,0,0,.1)',                               label: 'Small' },
      { value: '0 4px 16px rgba(0,0,0,.1)',                              label: 'Medium' },
      { value: '0 8px 32px rgba(0,0,0,.15)',                             label: 'Large' },
      { value: '0 24px 64px rgba(0,0,0,.2)',                             label: 'XL' },
    ],

    fontWeightOptions: [
      { value: '300', label: 'Light' },
      { value: '400', label: 'Regular' },
      { value: '500', label: 'Medium' },
      { value: '600', label: 'Semibold' },
      { value: '700', label: 'Bold' },
      { value: '800', label: 'Extrabold' },
      { value: '900', label: 'Black' },
    ],

    // Load styles from a block config
    loadFromBlock(blockStyles) {
      if (!blockStyles) return;
      Object.assign(this.styles, blockStyles);
    },

    // Export styles back to block config format
    toBlockStyles() {
      return { ...this.styles };
    },

    // Build inline CSS string for preview
    toCss() {
      const s = this.styles;
      const bg = s.bgType === 'transparent' ? 'transparent'
               : s.bgType === 'gradient'    ? `linear-gradient(135deg, var(--primary), var(--secondary))`
               : s.bgColor;
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

    // Push style update to iframe via postMessage
    pushToFrame(frame, blockId) {
      try {
        frame.contentWindow.postMessage({
          type:    'wbs:style-update',
          blockId: blockId,
          css:     this.toCss(),
        }, '*');
      } catch(e) {}
    },
  };
}

// ── Rich text toolbar ─────────────────────────────────────────────────────────

const RICH_TEXT_TOOLBAR_HTML = `
<div id="wbs-rte-toolbar" style="
  display:none;position:fixed;z-index:99999;
  background:#1e1b4b;border-radius:.5rem;padding:.3rem .4rem;
  box-shadow:0 8px 24px rgba(0,0,0,.3);
  display:flex;gap:.15rem;align-items:center;
  pointer-events:auto;
" onmousedown="event.preventDefault()">
  <button onclick="wbsRte('bold')"      title="Bold (Ctrl+B)"   style="background:none;border:none;color:#c4b5fd;cursor:pointer;padding:.25rem .4rem;border-radius:.25rem;font-weight:700;font-size:.85rem" onmouseover="this.style.background='rgba(255,255,255,.15)'" onmouseout="this.style.background='none'">B</button>
  <button onclick="wbsRte('italic')"    title="Italic (Ctrl+I)" style="background:none;border:none;color:#c4b5fd;cursor:pointer;padding:.25rem .4rem;border-radius:.25rem;font-style:italic;font-size:.85rem" onmouseover="this.style.background='rgba(255,255,255,.15)'" onmouseout="this.style.background='none'">I</button>
  <button onclick="wbsRte('underline')" title="Underline"       style="background:none;border:none;color:#c4b5fd;cursor:pointer;padding:.25rem .4rem;border-radius:.25rem;text-decoration:underline;font-size:.85rem" onmouseover="this.style.background='rgba(255,255,255,.15)'" onmouseout="this.style.background='none'">U</button>
  <div style="width:1px;height:16px;background:rgba(255,255,255,.2);margin:0 .15rem"></div>
  <button onclick="wbsRteLink()"        title="Link"            style="background:none;border:none;color:#c4b5fd;cursor:pointer;padding:.25rem .4rem;border-radius:.25rem;font-size:.85rem" onmouseover="this.style.background='rgba(255,255,255,.15)'" onmouseout="this.style.background='none'">🔗</button>
  <button onclick="wbsRteClear()"       title="Clear formatting" style="background:none;border:none;color:#c4b5fd;cursor:pointer;padding:.25rem .4rem;border-radius:.25rem;font-size:.85rem" onmouseover="this.style.background='rgba(255,255,255,.15)'" onmouseout="this.style.background='none'">✕</button>
</div>`;

// Inject the toolbar into the page once
function initRichTextToolbar() {
  if (document.getElementById('wbs-rte-toolbar')) return;
  document.body.insertAdjacentHTML('beforeend', RICH_TEXT_TOOLBAR_HTML);
}

// Show toolbar near a selection
function showRteToolbar(x, y) {
  const tb = document.getElementById('wbs-rte-toolbar');
  if (!tb) return;
  tb.style.display = 'flex';
  tb.style.left = Math.min(x, window.innerWidth - 220) + 'px';
  tb.style.top  = (y - 48) + 'px';
}

function hideRteToolbar() {
  const tb = document.getElementById('wbs-rte-toolbar');
  if (tb) tb.style.display = 'none';
}

// Execute rich text command
window.wbsRte = function(cmd) {
  document.execCommand(cmd, false, null);
};

window.wbsRteLink = function() {
  const url = prompt('Enter URL:', 'https://');
  if (url) document.execCommand('createLink', false, url);
};

window.wbsRteClear = function() {
  document.execCommand('removeFormat', false, null);
  document.execCommand('unlink', false, null);
};

// Listen for selection changes to show/hide toolbar
document.addEventListener('selectionchange', () => {
  const sel = window.getSelection();
  if (!sel || sel.isCollapsed || !sel.toString().trim()) {
    hideRteToolbar();
    return;
  }
  // Only show if selection is inside a contenteditable
  const node = sel.anchorNode?.parentElement;
  if (node?.isContentEditable) {
    const rect = sel.getRangeAt(0).getBoundingClientRect();
    showRteToolbar(rect.left + rect.width / 2 - 100, rect.top + window.scrollY);
  }
});

document.addEventListener('mousedown', e => {
  if (!e.target.closest('#wbs-rte-toolbar')) hideRteToolbar();
});
