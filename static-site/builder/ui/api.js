/**
 * api.js v2 — All backend API calls.
 *
 * Every function returns { ok, data, error }.
 * Handles:
 *   - Auth session (redirect to /login on 401)
 *   - CSRF token (X-CSRF-Token header on all mutating requests)
 *   - New { success, data, error } envelope from server v6
 *   - Backward compat with old { ok, ... } envelope
 */
'use strict';

// ── CSRF token management ─────────────────────────────────────────────────────
const CSRF = {
  get()        { return localStorage.getItem('wbs_csrf') || ''; },
  set(token)   { if (token) localStorage.setItem('wbs_csrf', token); },
  clear()      { localStorage.removeItem('wbs_csrf'); },

  /** Refresh token from server (called after login and on 403). */
  async refresh() {
    try {
      const res  = await fetch('/api/auth/csrf');
      const data = await res.json();
      const tok  = data?.data?.csrf_token || data?.csrf_token;
      if (tok) this.set(tok);
      return tok;
    } catch(_) { return ''; }
  },
};

// ── Internal fetch wrapper ────────────────────────────────────────────────────
async function _req(url, opts = {}, retry = true) {
  // Attach CSRF header for mutating methods
  const method = (opts.method || 'GET').toUpperCase();
  if (['POST','PUT','DELETE','PATCH'].includes(method)) {
    opts.headers = opts.headers || {};
    opts.headers['X-CSRF-Token'] = CSRF.get();
  }

  try {
    const res = await fetch(url, opts);
    const ct  = res.headers.get('content-type') || '';
    let   raw;
    if (ct.includes('application/json')) {
      raw = await res.json();
    } else if (!res.ok) {
      return { ok: false, error: `HTTP ${res.status}`, data: null };
    } else {
      // Binary (zip download etc.)
      return { ok: true, data: await res.blob(), error: null };
    }

    // Handle 401 — redirect to login
    if (res.status === 401) {
      CSRF.clear();
      window.location.href = '/login';
      return { ok: false, error: 'Authentication required', data: null };
    }

    // Handle 403 — try refreshing CSRF once
    if (res.status === 403 && retry) {
      await CSRF.refresh();
      return _req(url, opts, false);
    }

    // Normalise envelope: server v6 uses { success, data, error }
    // Older routes may return { ok, ... } directly
    if ('success' in raw) {
      // Store any new CSRF token the server sends back
      if (raw.data?.csrf_token) CSRF.set(raw.data.csrf_token);
      return { ok: raw.success, data: raw.data || {}, error: raw.error || '' };
    }
    // Legacy envelope
    if ('ok' in raw) {
      return { ok: raw.ok, data: raw, error: raw.error || '' };
    }
    return { ok: res.ok, data: raw, error: '' };

  } catch(e) {
    return { ok: false, error: 'Server offline', data: null };
  }
}

function _json(body) {
  return {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(body),
  };
}

// ── Public API object ─────────────────────────────────────────────────────────
const API = {

  // ── Auth ───────────────────────────────────────────────────────────────────

  async register(email, password) {
    return _req('/api/auth/register', _json({ email, password }));
  },

  async login(email, password) {
    const r = await _req('/api/auth/login', _json({ email, password }));
    if (r.ok && r.data?.csrf_token) CSRF.set(r.data.csrf_token);
    return r;
  },

  async logout() {
    const r = await _req('/api/auth/logout', { method: 'POST' });
    CSRF.clear();
    return r;
  },

  async me() {
    const r = await _req('/api/auth/me');
    if (r.ok && r.data?.csrf_token) CSRF.set(r.data.csrf_token);
    return r;
  },

  // ── Projects ───────────────────────────────────────────────────────────────

  async listProjects() {
    return _req('/api/projects');
  },

  async createProject(name, config) {
    return _req('/api/projects', _json({ name, config }));
  },

  async getProject(pid) {
    return _req(`/api/projects/${pid}`);
  },

  async updateProject(pid, { config, name } = {}) {
    return _req(`/api/projects/${pid}`, {
      method:  'PUT',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ config, name }),
    });
  },

  async deleteProject(pid) {
    return _req(`/api/projects/${pid}`, { method: 'DELETE' });
  },

  async duplicateProject(pid) {
    return _req(`/api/projects/${pid}/duplicate`, { method: 'POST' });
  },

  // ── Publish ────────────────────────────────────────────────────────────────

  async publish(pid) {
    return _req(`/api/publish/${pid}`, { method: 'POST' });
  },

  async publishStatus(jid) {
    return _req(`/api/publish/status/${jid}`);
  },

  async listVersions(pid) {
    return _req(`/api/publish/${pid}/versions`);
  },

  async rollback(pid, ver) {
    return _req(`/api/publish/${pid}/rollback/${ver}`, { method: 'POST' });
  },

  // ── Preview ────────────────────────────────────────────────────────────────

  async preview(config, page, visual = true) {
    return _req('/api/preview', _json({ config, page, visual }));
  },

  async previewUrl(config, projectId) {
    return _req('/api/preview-url', _json({ config, project_id: projectId }));
  },

  // ── Export ─────────────────────────────────────────────────────────────────

  async exportZip(config, mode) {
    try {
      const res = await fetch('/api/export', {
        ..._json({ config, mode, minify: false }),
        headers: {
          'Content-Type':  'application/json',
          'X-CSRF-Token':  CSRF.get(),
        },
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        return { ok: false, error: err.error || `HTTP ${res.status}`, data: null };
      }
      return { ok: true, data: await res.blob(), error: null };
    } catch(e) {
      return { ok: false, error: 'Server offline', data: null };
    }
  },

  // ── Upload ─────────────────────────────────────────────────────────────────

  async upload(file, projectId) {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('project_id', projectId || 'global');
    return _req('/api/upload', {
      method:  'POST',
      headers: { 'X-CSRF-Token': CSRF.get() },
      body:    fd,
    });
  },

  async listUploads(pid) {
    return _req(`/api/upload/${pid}/list`);
  },

  async cleanupUploads(pid) {
    return _req(`/api/upload/${pid}/cleanup`, { method: 'POST' });
  },

  // ── Legacy ─────────────────────────────────────────────────────────────────

  async saveConfig(config) {
    return _req('/api/save', _json({ config }));
  },
};
