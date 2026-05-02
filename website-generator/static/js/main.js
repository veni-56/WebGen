/**
 * main.js — WebGen Platform
 * Platform-level JS: nav menu, flash auto-dismiss.
 */

// ── Nav user dropdown ─────────────────────────────────────────────────────────
function toggleUserMenu() {
  document.getElementById('userDropdown')?.classList.toggle('open');
}
document.addEventListener('click', e => {
  if (!e.target.closest('.nav-user-menu')) {
    document.getElementById('userDropdown')?.classList.remove('open');
  }
});

// ── Auto-dismiss flash messages ───────────────────────────────────────────────
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .5s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  }, 4000);
});
