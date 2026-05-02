/* ============================================================
   script.js — Static Pro Global Scripts
   Generator compatible: {{site_name}} {{primary_color}}
   ============================================================ */

'use strict';

// ── 1. Component loader ───────────────────────────────────────
async function loadComponent(id, url) {
  try {
    const res  = await fetch(url);
    const html = await res.text();
    const el   = document.getElementById(id);
    if (el) {
      el.innerHTML = html;
      // Re-init Alpine on injected content
      if (window.Alpine) Alpine.initTree(el);
      // Re-run active nav highlight after navbar loads
      if (id === 'navbar') highlightActiveNav();
    }
  } catch (e) {
    console.warn(`Component load failed: ${url}`, e);
  }
}

// Detect component base path (works from root or /pages/)
const isInPages = location.pathname.includes('/pages/');
const base = isInPages ? '../' : './';

document.addEventListener('DOMContentLoaded', () => {
  loadComponent('navbar', base + 'components/navbar.html');
  loadComponent('footer', base + 'components/footer.html');
});

// ── 2. Dark mode ──────────────────────────────────────────────
function applyDark(isDark) {
  document.documentElement.classList.toggle('dark', isDark);
  const sun  = document.getElementById('iconSun');
  const moon = document.getElementById('iconMoon');
  if (sun)  sun.classList.toggle('hidden', !isDark);
  if (moon) moon.classList.toggle('hidden', isDark);
}

function toggleDark() {
  const isDark = !document.documentElement.classList.contains('dark');
  localStorage.setItem('dark', isDark);
  applyDark(isDark);
}

// Apply on load
applyDark(localStorage.getItem('dark') === 'true');

// ── 3. Scroll progress bar ────────────────────────────────────
const progressBar = document.getElementById('scrollProgress');
window.addEventListener('scroll', () => {
  const scrolled = window.scrollY;
  const total    = document.documentElement.scrollHeight - window.innerHeight;
  const pct      = total > 0 ? (scrolled / total) : 0;
  if (progressBar) progressBar.style.transform = `scaleX(${pct})`;

  // Back to top visibility
  const btn = document.getElementById('backToTop');
  if (btn) btn.classList.toggle('visible', scrolled > 400);

  // Navbar shadow
  const nav = document.getElementById('mainNav');
  if (nav) nav.style.boxShadow = scrolled > 8 ? '0 4px 24px rgba(0,0,0,.12)' : 'none';
}, { passive: true });

// ── 4. Scroll reveal ──────────────────────────────────────────
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      revealObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

function initReveal() {
  document.querySelectorAll('.reveal, .reveal-left, .reveal-right')
    .forEach(el => revealObserver.observe(el));
}
document.addEventListener('DOMContentLoaded', initReveal);

// ── 5. Counter animation ──────────────────────────────────────
function animateCounter(el) {
  const target = parseInt(el.dataset.target);
  const suffix = el.dataset.suffix || '';
  let count = 0;
  const step = Math.ceil(target / 60);
  const timer = setInterval(() => {
    count = Math.min(count + step, target);
    el.textContent = count.toLocaleString() + suffix;
    if (count >= target) clearInterval(timer);
  }, 22);
}

const counterObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.querySelectorAll('[data-target]').forEach(animateCounter);
      counterObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.4 });

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.stats-row').forEach(el => counterObserver.observe(el));
});

// ── 6. Active nav highlight ───────────────────────────────────
function highlightActiveNav() {
  const page = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-link').forEach(a => {
    const href = (a.getAttribute('href') || '').split('/').pop();
    if (href === page || (page === '' && href === 'index.html')) {
      a.classList.add('active');
    }
  });
}

// ── 7. Toast notification ─────────────────────────────────────
window.showToast = function(msg, type = 'success') {
  const colors = {
    success: 'bg-emerald-500',
    error:   'bg-red-500',
    info:    'bg-blue-500',
    warning: 'bg-amber-500',
  };
  const t = document.createElement('div');
  t.className = `fixed bottom-6 right-6 z-[9999] px-5 py-3 rounded-2xl text-white text-sm font-semibold
                 shadow-2xl toast-enter flex items-center gap-2 ${colors[type] || colors.success}`;
  t.innerHTML = `<span>${msg}</span>
    <button onclick="this.parentElement.remove()" class="ml-2 opacity-70 hover:opacity-100 text-lg leading-none" aria-label="Close">×</button>`;
  document.body.appendChild(t);
  setTimeout(() => {
    t.classList.add('toast-leave');
    setTimeout(() => t.remove(), 300);
  }, 3500);
};

// ── 8. Contact form ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const cf = document.getElementById('contactForm');
  if (cf) {
    cf.addEventListener('submit', e => {
      e.preventDefault();
      const btn = cf.querySelector('[type=submit]');
      const orig = btn.textContent;
      btn.textContent = 'Sending…'; btn.disabled = true;
      setTimeout(() => {
        cf.reset();
        btn.textContent = orig; btn.disabled = false;
        showToast('Message sent! We\'ll get back to you soon. ✅');
      }, 1200);
    });
  }
});

// ── 9. Smooth anchor scroll ───────────────────────────────────
document.addEventListener('click', e => {
  const a = e.target.closest('a[href^="#"]');
  if (!a) return;
  const target = document.querySelector(a.getAttribute('href'));
  if (target) {
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
});
