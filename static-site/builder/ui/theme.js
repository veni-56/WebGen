/**
 * theme.js — Advanced Theme System
 * Generates full color palettes (50–900 shades), applies CSS vars globally,
 * pushes theme to preview iframe, supports dark mode tokens.
 */
'use strict';

// ── Color math ────────────────────────────────────────────────────────────────

function hexToHsl(hex) {
  let r = parseInt(hex.slice(1,3),16)/255;
  let g = parseInt(hex.slice(3,5),16)/255;
  let b = parseInt(hex.slice(5,7),16)/255;
  const max = Math.max(r,g,b), min = Math.min(r,g,b);
  let h, s, l = (max+min)/2;
  if (max === min) { h = s = 0; }
  else {
    const d = max - min;
    s = l > 0.5 ? d/(2-max-min) : d/(max+min);
    switch(max) {
      case r: h = ((g-b)/d + (g<b?6:0))/6; break;
      case g: h = ((b-r)/d + 2)/6; break;
      case b: h = ((r-g)/d + 4)/6; break;
    }
  }
  return [Math.round(h*360), Math.round(s*100), Math.round(l*100)];
}

function hslToHex(h, s, l) {
  s /= 100; l /= 100;
  const a = s * Math.min(l, 1-l);
  const f = n => {
    const k = (n + h/30) % 12;
    const c = l - a * Math.max(Math.min(k-3, 9-k, 1), -1);
    return Math.round(255*c).toString(16).padStart(2,'0');
  };
  return `#${f(0)}${f(8)}${f(4)}`;
}

function hexToRgb(hex) {
  return [parseInt(hex.slice(1,3),16), parseInt(hex.slice(3,5),16), parseInt(hex.slice(5,7),16)];
}

// Generate 11 shades (50, 100, 200, ... 900) from a base hex color
function generateShades(hex) {
  const [h, s] = hexToHsl(hex);
  const stops = [
    [50,  97], [100, 94], [200, 88], [300, 78],
    [400, 65], [500, 52], [600, 42], [700, 33],
    [800, 25], [900, 18]
  ];
  const result = {};
  stops.forEach(([name, l]) => { result[name] = hslToHex(h, Math.min(s, 85), l); });
  return result;
}

// ── Theme presets ─────────────────────────────────────────────────────────────

const THEME_PRESETS = [
  { name: 'Violet', primary: '#6c63ff', secondary: '#f50057', bg: '#ffffff', text: '#111827' },
  { name: 'Ocean',  primary: '#0277bd', secondary: '#00bcd4', bg: '#f0f9ff', text: '#0c1a2e' },
  { name: 'Forest', primary: '#2e7d32', secondary: '#ffc107', bg: '#f0fdf4', text: '#14532d' },
  { name: 'Sunset', primary: '#e65100', secondary: '#f50057', bg: '#fff7ed', text: '#431407' },
  { name: 'Dark',   primary: '#bb86fc', secondary: '#03dac6', bg: '#0f0f1a', text: '#e2e8f0' },
  { name: 'Gold',   primary: '#b8860b', secondary: '#8b0000', bg: '#fffbeb', text: '#1c1917' },
  { name: 'Rose',   primary: '#e11d48', secondary: '#7c3aed', bg: '#fff1f2', text: '#1c0a0e' },
  { name: 'Slate',  primary: '#475569', secondary: '#0ea5e9', bg: '#f8fafc', text: '#0f172a' },
];

// ── CSS variable generation ───────────────────────────────────────────────────

function buildThemeCss(theme) {
  const pShades = generateShades(theme.primary);
  const sShades = generateShades(theme.secondary);
  const [pr, pg, pb] = hexToRgb(theme.primary);
  const [sr, sg, sb] = hexToRgb(theme.secondary);

  let css = ':root {\n';
  css += `  --primary: ${theme.primary};\n`;
  css += `  --secondary: ${theme.secondary};\n`;
  css += `  --bg: ${theme.bg || '#ffffff'};\n`;
  css += `  --text: ${theme.text || '#111827'};\n`;
  css += `  --primary-rgb: ${pr},${pg},${pb};\n`;
  css += `  --secondary-rgb: ${sr},${sg},${sb};\n`;
  css += `  --font: '${theme.font || 'Inter'}', system-ui, sans-serif;\n`;

  Object.entries(pShades).forEach(([k, v]) => { css += `  --primary-${k}: ${v};\n`; });
  Object.entries(sShades).forEach(([k, v]) => { css += `  --secondary-${k}: ${v};\n`; });
  css += '}\n';

  // Dark mode override
  if (theme.dark_mode) {
    css += `\n@media (prefers-color-scheme: dark) {\n  :root {\n    --bg: #0f0f1a;\n    --text: #e2e8f0;\n  }\n}\n`;
  }

  return css;
}

// Apply theme to the builder UI itself
function applyThemeToBuilder(theme) {
  let el = document.getElementById('wbs-builder-theme');
  if (!el) {
    el = document.createElement('style');
    el.id = 'wbs-builder-theme';
    document.head.appendChild(el);
  }
  el.textContent = buildThemeCss(theme);

  // Google Font
  let fl = document.getElementById('wbs-font');
  if (!fl) { fl = document.createElement('link'); fl.id = 'wbs-font'; fl.rel = 'stylesheet'; document.head.appendChild(fl); }
  fl.href = `https://fonts.googleapis.com/css2?family=${(theme.font||'Inter').replace(/ /g,'+')}:wght@400;500;600;700;800&display=swap`;
}

// Push theme CSS into preview iframe
function pushThemeToIframe(frame, theme) {
  try {
    frame.contentWindow.postMessage({
      type: 'wbs:theme',
      css:  buildThemeCss(theme)
    }, '*');
  } catch(e) {}
}

// Build a full theme object from primary + secondary colors
function buildTheme(primary, secondary, font, bg, text, darkMode) {
  return {
    primary:   primary   || '#6c63ff',
    secondary: secondary || '#f50057',
    font:      font      || 'Inter',
    bg:        bg        || '#ffffff',
    text:      text      || '#111827',
    dark_mode: !!darkMode,
    shades: {
      primary:   generateShades(primary   || '#6c63ff'),
      secondary: generateShades(secondary || '#f50057'),
    }
  };
}
