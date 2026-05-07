#!/usr/bin/env python3
"""
server.py v6 -- Production SaaS Website Builder Backend
Auth, project ownership, slugs, background builds, rate limiting, CSRF.
"""
import hashlib, json, os, queue, re, secrets, shutil, sqlite3
import tempfile, threading, time, uuid
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

from flask import (Flask, abort, g, jsonify, request,
                   send_file, send_from_directory, session)

# Optional: bcrypt (falls back to sha256 if not installed)
try:
    import bcrypt
    _BCRYPT = True
except ImportError:
    _BCRYPT = False

# Optional: python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# â”€â”€ Paths â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
BUILDER_DIR = Path(__file__).parent.parent
UI_DIR      = Path(__file__).parent
UPLOADS_DIR = Path(os.environ.get("UPLOADS_DIR", str(UI_DIR / "uploads")))
PUBLISH_DIR = Path(os.environ.get("PUBLISH_DIR", str(UI_DIR / "published")))
DB_PATH     = Path(os.environ.get("DB_PATH",     str(UI_DIR / "projects.db")))

import sys
sys.path.insert(0, str(BUILDER_DIR))
from build import build

UPLOADS_DIR.mkdir(exist_ok=True)
PUBLISH_DIR.mkdir(exist_ok=True)

# â”€â”€ Flask app â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
app = Flask(__name__, static_folder=str(UI_DIR))
app.secret_key          = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024   # 32 MB upload limit
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# â”€â”€ Constants â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ALLOWED_EXT      = {"png", "jpg", "jpeg", "gif", "webp", "svg"}
MAX_FILE_BYTES   = 8 * 1024 * 1024   # 8 MB per upload
MAX_NAME_LEN     = 120
_TAG_RE          = re.compile(r"<[^>]+>")
_SLUG_RE         = re.compile(r"^[a-z0-9][a-z0-9-]{1,60}[a-z0-9]$")

# â”€â”€ Rate limiter (in-memory token bucket, no Redis needed) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_rl_lock    = threading.Lock()
_rl_buckets: dict[str, dict] = {}   # key -> {tokens, last_refill}

def _rate_check(key: str, capacity: int = 10, refill_per_min: int = 10) -> bool:
    """Return True if request is allowed, False if rate-limited."""
    now = time.monotonic()
    with _rl_lock:
        b = _rl_buckets.setdefault(key, {"tokens": capacity, "last": now})
        elapsed = now - b["last"]
        b["tokens"] = min(capacity, b["tokens"] + elapsed * (refill_per_min / 60))
        b["last"]   = now
        if b["tokens"] >= 1:
            b["tokens"] -= 1
            return True
        return False

def rate_limit(capacity: int = 10, per_min: int = 10):
    """Decorator: rate-limit by IP. Returns 429 if exceeded."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            key = f"{fn.__name__}:{request.remote_addr}"
            if not _rate_check(key, capacity, per_min):
                return R.err("Rate limit exceeded. Try again shortly.", 429)
            return fn(*a, **kw)
        return wrapper
    return decorator

# â”€â”€ Response envelope â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class R:
    """Consistent JSON envelope: {success, data, error}"""
    @staticmethod
    def ok(data=None, status=200):
        return jsonify({"success": True,  "data": data or {}, "error": ""}), status

    @staticmethod
    def err(msg: str, status=400):
        return jsonify({"success": False, "data": {},          "error": msg}), status

# â”€â”€ Password helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _hash_pw(pw: str) -> str:
    if _BCRYPT:
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    # Fallback: PBKDF2-HMAC-SHA256 (stdlib)
    salt = secrets.token_hex(16)
    dk   = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 260_000)
    return f"pbkdf2:{salt}:{dk.hex()}"

def _check_pw(pw: str, stored: str) -> bool:
    if _BCRYPT and stored.startswith("$2"):
        return bcrypt.checkpw(pw.encode(), stored.encode())
    if stored.startswith("pbkdf2:"):
        _, salt, dk_hex = stored.split(":", 2)
        dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 260_000)
        return secrets.compare_digest(dk.hex(), dk_hex)
    return False

# â”€â”€ Input validation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _require(data: dict, *keys):
    """Return (value, ...) or raise ValueError with missing key name."""
    out = []
    for k in keys:
        v = data.get(k)
        if v is None or (isinstance(v, str) and not v.strip()):
            raise ValueError(f"'{k}' is required")
        out.append(v.strip() if isinstance(v, str) else v)
    return out[0] if len(out) == 1 else tuple(out)

def sanitize(s: str, max_len: int = 2000) -> str:
    return _TAG_RE.sub("", str(s or ""))[:max_len].strip()

def _valid_email(e: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e))

# â”€â”€ Config hashing â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def cfg_hash(cfg: dict) -> str:
    return hashlib.sha256(
        json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()[:16]

# â”€â”€ Preview cache â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_preview_cache: dict[str, str] = {}
_CACHE_MAX = 40

def _cache_key(cfg, page, visual):
    return f"{cfg_hash(cfg)}:{page}:{int(visual)}"

def _cache_get(k):
    return _preview_cache.get(k)

def _cache_set(k, html):
    if len(_preview_cache) >= _CACHE_MAX:
        _preview_cache.pop(next(iter(_preview_cache)))
    _preview_cache[k] = html

# â”€â”€ Background build queue (replaced by persistent JobQueue in worker.py) â”€â”€â”€â”€â”€
# Legacy in-memory structures kept for backward compat with any direct references
import queue as _queue_mod
_build_queue: _queue_mod.Queue = _queue_mod.Queue(maxsize=0)   # unused sentinel
_build_results: dict[str, dict] = {}   # legacy fallback (JobQueue is primary)

def _build_worker():
    pass   # replaced by WorkerPool in worker.py

_worker_thread = None   # replaced by WorkerPool

def _enqueue_build(fn, *args, **kwargs) -> str:
    """
    Legacy shim: wraps a callable into a JobQueue job.
    Determines job type from the function name.
    """
    from worker import JobQueue
    # Infer job type from function name
    name = getattr(fn, "__name__", "")
    if "publish" in name:
        jtype = "publish"
    elif "preview" in name:
        jtype = "preview"
    else:
        jtype = "export"

    # Serialise args/kwargs into payload
    # Functions receive (cfg, pid) or (cfg,) â€” we store them as JSON
    payload = {"_fn": name}
    if args:
        try:
            import json as _j
            _j.dumps(args[0])   # test serializability
            payload["cfg"] = args[0]
        except Exception:
            pass
    if len(args) > 1:
        payload["pid"] = args[1]
    payload.update(kwargs)

    # Register the function as a handler if not already registered
    if jtype not in JobQueue._handlers:
        def _make_handler(_fn, _args, _kwargs):
            def _h(p):
                return _fn(*_args, **_kwargs)
            return _h
        JobQueue.register_handler(jtype, _make_handler(fn, args, kwargs))
    else:
        # Update handler to latest function (handles re-patching)
        _a, _kw = args, kwargs
        def _h(p):
            return fn(*_a, **_kw)
        JobQueue.register_handler(jtype, _h)

    jid = JobQueue.enqueue(jtype, payload)
    return jid

# -- Job queue size helper (replaces _build_queue.qsize()) --
def _job_queue_size() -> int:
    try:
        from worker import JobQueue
        stats = JobQueue.queue_stats()
        return stats.get("queued", 0) + stats.get("running", 0)
    except Exception:
        return 0

# -- Bootstrap persistent job queue + worker pool --
def _bootstrap_workers() -> None:
    try:
        from worker import JobQueue, pool
        JobQueue.configure(DB_PATH)
        recovered = JobQueue._recover_stuck()
        if recovered:
            print(f"[WORKER] Recovered {recovered} stuck job(s)", flush=True)
        n = int(os.environ.get("WORKER_COUNT", "2"))
        pool.start(n_workers=n)
        print(f"[WORKER] {n} worker(s) started", flush=True)
    except Exception as e:
        print(f"[WORKER] Bootstrap failed: {e}", flush=True)

_bootstrap_workers()


# â”€â”€ Bridge script (injected into preview pages) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
BRIDGE = """<script>
(function(){
  const MSG={
    SELECT:'wbs:select',DESELECT:'wbs:deselect',ACTION:'wbs:action',
    TEXT_EDIT:'wbs:text-edit',IMAGE_CLICK:'wbs:image-click',
    THEME:'wbs:theme',HIGHLIGHT:'wbs:highlight',REPLACE_IMAGE:'wbs:replace-image'
  };
  let sel=null;
  const st=document.createElement('style');
  st.textContent=`
    [data-wbs]{position:relative;cursor:pointer;transition:outline .12s,box-shadow .12s}
    [data-wbs]:hover{outline:2px dashed rgba(108,99,255,.45);outline-offset:3px}
    [data-wbs].wbs-sel{outline:2.5px solid #6c63ff!important;outline-offset:3px;box-shadow:0 0 0 4px rgba(108,99,255,.15)!important}
    .wbs-label{position:absolute;top:-22px;left:0;background:#6c63ff;color:#fff;font-size:10px;font-weight:700;padding:2px 7px;border-radius:4px 4px 0 0;letter-spacing:.04em;pointer-events:none;z-index:9999;white-space:nowrap}
    .wbs-tb{position:absolute;top:-22px;right:0;display:flex;gap:2px;background:#1e1b4b;border-radius:4px;padding:2px 4px;z-index:9999;opacity:0;transition:opacity .15s;pointer-events:none}
    [data-wbs]:hover .wbs-tb,[data-wbs].wbs-sel .wbs-tb{opacity:1;pointer-events:auto}
    .wbs-tb button{background:none;border:none;color:#c4b5fd;cursor:pointer;font-size:11px;padding:1px 5px;border-radius:3px;line-height:1.4}
    .wbs-tb button:hover{background:rgba(255,255,255,.15);color:#fff}
    [contenteditable]:focus{outline:2px solid #6c63ff;outline-offset:1px;border-radius:2px;background:rgba(108,99,255,.04)}
  `;
  document.head.appendChild(st);
  function tag(){
    const counts={};
    ['section','header','footer','nav','article','aside','main'].forEach(t=>{
      document.querySelectorAll(t).forEach(el=>{
        if(el.dataset.wbs) return;
        counts[t]=(counts[t]||0)+1;
        const sid=el.dataset.sectionId||`${t}_${counts[t]}`;
        el.dataset.wbs=sid; el.style.position='relative';
        const lb=document.createElement('div'); lb.className='wbs-label';
        lb.textContent=el.dataset.sectionName||t+(counts[t]>1?' '+counts[t]:'');
        el.appendChild(lb);
        const tb=document.createElement('div'); tb.className='wbs-tb';
        tb.innerHTML='<button title="Edit" onclick="wbsSel(this.closest(\'[data-wbs]\'))">&#9998;</button>'+
          '<button title="Dup" onclick="wbsAct(\'dup\',this.closest(\'[data-wbs]\').dataset.wbs)">&#10697;</button>'+
          '<button title="Hide" onclick="wbsAct(\'hide\',this.closest(\'[data-wbs]\').dataset.wbs)">&#128065;</button>'+
          '<button title="Del" onclick="wbsAct(\'del\',this.closest(\'[data-wbs]\').dataset.wbs)">&#10005;</button>';
        el.appendChild(tb);
      });
    });
  }
  window.wbsSel=function(el){if(sel)sel.classList.remove('wbs-sel');sel=el;el.classList.add('wbs-sel');parent.postMessage({type:MSG.SELECT,id:el.dataset.wbs,name:el.dataset.sectionName||el.dataset.wbs},'*');};
  window.wbsAct=function(action,id){parent.postMessage({type:MSG.ACTION,action,id},'*');};
  document.addEventListener('click',e=>{const el=e.target.closest('[data-wbs]');if(el){e.stopPropagation();wbsSel(el);}else{if(sel){sel.classList.remove('wbs-sel');sel=null;}parent.postMessage({type:MSG.DESELECT},'*');}},true);
  document.addEventListener('dblclick',e=>{const el=e.target;if(!['H1','H2','H3','H4','P','SPAN','A','LI','BUTTON'].includes(el.tagName))return;el.contentEditable='true';el.focus();const r=document.createRange();r.selectNodeContents(el);window.getSelection().removeAllRanges();window.getSelection().addRange(r);el.addEventListener('blur',function f(){el.contentEditable='false';el.removeEventListener('blur',f);parent.postMessage({type:MSG.TEXT_EDIT,tag:el.tagName,text:el.innerText,sec:el.closest('[data-wbs]')?.dataset.wbs},'*');},{once:true});el.addEventListener('keydown',function k(ev){if(ev.key==='Enter'){ev.preventDefault();el.blur();}if(ev.key==='Escape'){el.contentEditable='false';el.removeEventListener('keydown',k);}});});
  document.addEventListener('click',e=>{if(e.target.tagName==='IMG'&&e.altKey){e.preventDefault();parent.postMessage({type:MSG.IMAGE_CLICK,src:e.target.src,sec:e.target.closest('[data-wbs]')?.dataset.wbs},'*');}});
  window.addEventListener('message',e=>{const d=e.data;if(!d?.type)return;if(d.type===MSG.THEME){let s=document.getElementById('wbs-lt');if(!s){s=document.createElement('style');s.id='wbs-lt';document.head.appendChild(s);}s.textContent=d.css;}if(d.type===MSG.HIGHLIGHT){document.querySelectorAll('[data-wbs]').forEach(x=>x.classList.remove('wbs-sel'));const t=document.querySelector('[data-wbs="'+d.id+'"]');if(t){t.classList.add('wbs-sel');t.scrollIntoView({behavior:'smooth',block:'center'});}}if(d.type===MSG.REPLACE_IMAGE){document.querySelectorAll('img').forEach(img=>{if(img.src===d.oldSrc||img.src.endsWith(d.oldSrc))img.src=d.newSrc;});}if(d.type==='wbs:style-update'&&d.blockId){const el=document.querySelector('[data-block="'+d.blockId+'"]')||document.querySelector('[data-wbs="'+d.blockId+'"]');if(el&&d.css)el.setAttribute('style',(el.getAttribute('style')||'')+';'+d.css);}});
  document.readyState==='loading'?document.addEventListener('DOMContentLoaded',tag):tag();
})();
</script>"""

# â”€â”€ SQLite DB â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id           TEXT PRIMARY KEY,
            email        TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at   TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS projects (
            id           TEXT PRIMARY KEY,
            user_id      TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name         TEXT NOT NULL,
            slug         TEXT UNIQUE,
            config       TEXT NOT NULL DEFAULT '{}',
            config_hash  TEXT DEFAULT '',
            published    INTEGER DEFAULT 0,
            publish_url  TEXT DEFAULT '',
            created_at   TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at   TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS publish_versions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            version    TEXT NOT NULL,
            url        TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS project_uploads (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            user_id    TEXT NOT NULL,
            filename   TEXT NOT NULL,
            url        TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS csrf_tokens (
            token      TEXT PRIMARY KEY,
            user_id    TEXT NOT NULL,
            expires_at TEXT NOT NULL
        );
    """)
    # Migrations for existing DBs
    for col_sql in [
        "ALTER TABLE projects ADD COLUMN user_id TEXT NOT NULL DEFAULT 'legacy'",
        "ALTER TABLE projects ADD COLUMN slug TEXT",
        "ALTER TABLE projects ADD COLUMN config_hash TEXT DEFAULT ''",
        "ALTER TABLE project_uploads ADD COLUMN user_id TEXT NOT NULL DEFAULT 'legacy'",
    ]:
        try:
            conn.execute(col_sql)
        except Exception:
            pass
    conn.commit()
    conn.close()

init_db()

# â”€â”€ Auth helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def current_user_id() -> str | None:
    return session.get("user_id")

def require_auth(fn):
    """Decorator: return 401 if not logged in."""
    @wraps(fn)
    def wrapper(*a, **kw):
        if not current_user_id():
            return R.err("Authentication required", 401)
        return fn(*a, **kw)
    return wrapper

def _issue_csrf() -> str:
    """Generate a CSRF token tied to the current session user."""
    uid   = current_user_id()
    token = secrets.token_urlsafe(32)
    exp   = (datetime.utcnow() + timedelta(hours=8)).isoformat()
    conn  = get_db()
    conn.execute("INSERT INTO csrf_tokens (token,user_id,expires_at) VALUES (?,?,?)", (token, uid, exp))
    conn.commit(); conn.close()
    return token

def _verify_csrf(token: str) -> bool:
    """Validate CSRF token belongs to current user and is not expired."""
    uid = current_user_id()
    if not uid or not token:
        return False
    conn = get_db()
    row  = conn.execute(
        "SELECT user_id,expires_at FROM csrf_tokens WHERE token=?", (token,)
    ).fetchone()
    conn.close()
    if not row:
        return False
    if row["user_id"] != uid:
        return False
    if datetime.fromisoformat(row["expires_at"]) < datetime.utcnow():
        return False
    return True

def csrf_protect(fn):
    """Decorator: verify X-CSRF-Token header on mutating requests."""
    @wraps(fn)
    def wrapper(*a, **kw):
        token = request.headers.get("X-CSRF-Token") or (request.get_json(silent=True) or {}).get("_csrf")
        if not _verify_csrf(token):
            return R.err("Invalid or missing CSRF token", 403)
        return fn(*a, **kw)
    return wrapper

# â”€â”€ Project ownership guard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _own_project(pid: str):
    """Return project row if it belongs to current user, else abort 403/404."""
    uid  = current_user_id()
    conn = get_db()
    row  = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    conn.close()
    if not row:
        abort(404)
    if row["user_id"] != uid:
        abort(403)
    return row

# â”€â”€ Build helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _inject_bridge(html: str) -> str:
    return html.replace("</body>", BRIDGE + "\n</body>", 1)

def _build_to_dir(cfg: dict, out_dir: Path, visual: bool = False):
    out_dir.mkdir(parents=True, exist_ok=True)
    build(cfg, out_dir, mode="static", minify=False)
    css = (out_dir / "style.css").read_text(encoding="utf-8") if (out_dir / "style.css").exists() else ""
    js  = (out_dir / "script.js").read_text(encoding="utf-8") if (out_dir / "script.js").exists() else ""
    for f in out_dir.glob("*.html"):
        html = f.read_text(encoding="utf-8")
        html = html.replace('<link rel="stylesheet" href="style.css"/>', f"<style>{css}</style>")
        html = html.replace('<script src="script.js"></script>', f"<script>{js}</script>")
        if visual:
            html = _inject_bridge(html)
        f.write_text(html, encoding="utf-8")

def _uploads_dir(uid: str, pid: str) -> Path:
    d = UPLOADS_DIR / uid / pid
    d.mkdir(parents=True, exist_ok=True)
    return d

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ROUTES
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# â”€â”€ Static UI â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/")
def index():
    return send_from_directory(str(UI_DIR), "index.html")

@app.route("/login")
def login_page():
    return send_from_directory(str(UI_DIR), "login.html")

@app.route("/register")
def register_page():
    return send_from_directory(str(UI_DIR), "register.html")

# â”€â”€ Auth â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/api/auth/register", methods=["POST"])
@rate_limit(capacity=5, per_min=5)
def auth_register():
    data = request.get_json(silent=True) or {}
    try:
        email, pw = _require(data, "email", "password")
    except ValueError as e:
        return R.err(str(e))
    email = email.lower().strip()
    if not _valid_email(email):
        return R.err("Invalid email address")
    if len(pw) < 8:
        return R.err("Password must be at least 8 characters")
    uid  = uuid.uuid4().hex[:16]
    conn = get_db()
    if conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
        conn.close()
        return R.err("Email already registered")
    conn.execute("INSERT INTO users (id,email,password_hash) VALUES (?,?,?)",
                 (uid, email, _hash_pw(pw)))
    conn.commit(); conn.close()
    session["user_id"] = uid
    csrf = _issue_csrf()
    return R.ok({"id": uid, "email": email, "csrf_token": csrf}, 201)

@app.route("/api/auth/login", methods=["POST"])
@rate_limit(capacity=10, per_min=10)
def auth_login():
    data = request.get_json(silent=True) or {}
    try:
        email, pw = _require(data, "email", "password")
    except ValueError as e:
        return R.err(str(e))
    email = email.lower().strip()
    conn  = get_db()
    row   = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    if not row or not _check_pw(pw, row["password_hash"]):
        return R.err("Invalid email or password", 401)
    session["user_id"] = row["id"]
    csrf = _issue_csrf()
    return R.ok({"id": row["id"], "email": row["email"], "csrf_token": csrf})

@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return R.ok({"message": "Logged out"})

@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    uid = current_user_id()
    if not uid:
        return R.err("Not authenticated", 401)
    conn = get_db()
    row  = conn.execute("SELECT id,email,created_at FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    if not row:
        session.clear()
        return R.err("User not found", 401)
    csrf = _issue_csrf()
    return R.ok({"id": row["id"], "email": row["email"], "created_at": row["created_at"], "csrf_token": csrf})

@app.route("/api/auth/csrf", methods=["GET"])
@require_auth
def get_csrf():
    return R.ok({"csrf_token": _issue_csrf()})

# â”€â”€ Projects CRUD (auth-scoped) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/api/projects", methods=["GET"])
@require_auth
def list_projects():
    uid  = current_user_id()
    conn = get_db()
    rows = conn.execute(
        "SELECT id,name,slug,published,publish_url,created_at,updated_at "
        "FROM projects WHERE user_id=? ORDER BY updated_at DESC", (uid,)
    ).fetchall()
    conn.close()
    return R.ok([dict(r) for r in rows])

@app.route("/api/projects", methods=["POST"])
@require_auth
@csrf_protect
def create_project():
    uid  = current_user_id()
    data = request.get_json(silent=True) or {}
    try:
        name = _require(data, "name")
    except ValueError as e:
        return R.err(str(e))
    name = sanitize(name, MAX_NAME_LEN)
    cfg  = data.get("config") or {}
    if not isinstance(cfg, dict):
        return R.err("config must be an object")
    pid  = uuid.uuid4().hex[:12]
    slug = _make_slug(name, pid)
    h    = cfg_hash(cfg)
    conn = get_db()
    conn.execute(
        "INSERT INTO projects (id,user_id,name,slug,config,config_hash) VALUES (?,?,?,?,?,?)",
        (pid, uid, name, slug, json.dumps(cfg), h)
    )
    conn.commit(); conn.close()
    return R.ok({"id": pid, "name": name, "slug": slug}, 201)

@app.route("/api/projects/<pid>", methods=["GET"])
@require_auth
def get_project(pid):
    row = _own_project(pid)
    d   = dict(row)
    d["config"] = json.loads(d["config"])
    return R.ok(d)

@app.route("/api/projects/<pid>", methods=["PUT"])
@require_auth
@csrf_protect
def update_project(pid):
    _own_project(pid)
    data = request.get_json(silent=True) or {}
    cfg  = data.get("config")
    name = data.get("name")
    conn = get_db()
    if cfg is not None:
        if not isinstance(cfg, dict):
            conn.close()
            return R.err("config must be an object")
        new_hash = cfg_hash(cfg)
        row = conn.execute("SELECT config_hash FROM projects WHERE id=?", (pid,)).fetchone()
        if row and row["config_hash"] == new_hash and not name:
            conn.close()
            return R.ok({"skipped": True})
        if name:
            conn.execute(
                "UPDATE projects SET config=?,name=?,config_hash=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (json.dumps(cfg), sanitize(name, MAX_NAME_LEN), new_hash, pid)
            )
        else:
            conn.execute(
                "UPDATE projects SET config=?,config_hash=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (json.dumps(cfg), new_hash, pid)
            )
    elif name:
        conn.execute(
            "UPDATE projects SET name=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (sanitize(name, MAX_NAME_LEN), pid)
        )
    conn.commit(); conn.close()
    return R.ok({})

@app.route("/api/projects/<pid>", methods=["DELETE"])
@require_auth
@csrf_protect
def delete_project(pid):
    _own_project(pid)
    conn = get_db()
    conn.execute("DELETE FROM projects WHERE id=?", (pid,))
    conn.commit(); conn.close()
    for d in [UPLOADS_DIR / current_user_id() / pid, PUBLISH_DIR / pid]:
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
    return R.ok({})

@app.route("/api/projects/<pid>/duplicate", methods=["POST"])
@require_auth
@csrf_protect
def duplicate_project(pid):
    uid = current_user_id()
    row = _own_project(pid)
    new_id   = uuid.uuid4().hex[:12]
    new_name = dict(row)["name"] + " (Copy)"
    new_slug = _make_slug(new_name, new_id)
    conn = get_db()
    conn.execute(
        "INSERT INTO projects (id,user_id,name,slug,config,config_hash) VALUES (?,?,?,?,?,?)",
        (new_id, uid, new_name, new_slug, row["config"], row["config_hash"] or "")
    )
    conn.commit(); conn.close()
    return R.ok({"id": new_id, "name": new_name, "slug": new_slug}, 201)

def _make_slug(name: str, pid: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40] or "site"
    slug = base
    conn = get_db()
    if conn.execute("SELECT id FROM projects WHERE slug=?", (slug,)).fetchone():
        slug = f"{base}-{pid[:6]}"
    conn.close()
    return slug

# â”€â”€ Preview (srcdoc, cached) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/api/preview", methods=["POST"])
@require_auth
@rate_limit(capacity=20, per_min=20)
def api_preview():
    data   = request.get_json(silent=True) or {}
    cfg    = data.get("config")
    page   = sanitize(data.get("page", "home"), 60)
    visual = bool(data.get("visual", True))
    if not isinstance(cfg, dict):
        return R.err("config must be an object")
    key    = _cache_key(cfg, page, visual)
    cached = _cache_get(key)
    if cached:
        return R.ok({"html": cached, "cached": True, "build_ms": 0})
    t0 = time.time()
    try:
        tmp      = Path(tempfile.gettempdir()) / f"wbs_srcdoc_{cfg_hash(cfg)}"
        _build_to_dir(cfg, tmp, visual=visual)
        filename = cfg.get("pages", {}).get(page, {}).get("file", "index.html")
        f = tmp / filename
        if not f.exists():
            f = tmp / "index.html"
        html = f.read_text(encoding="utf-8")
        _cache_set(key, html)
        return R.ok({"html": html, "cached": False, "build_ms": round((time.time()-t0)*1000)})
    except Exception as e:
        return R.err(str(e), 500)

# â”€â”€ Preview URL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/api/preview-url", methods=["POST"])
@require_auth
@rate_limit(capacity=10, per_min=10)
def api_preview_url():
    data = request.get_json(silent=True) or {}
    cfg  = data.get("config")
    pid  = sanitize(data.get("project_id", "default"), 40)
    if not isinstance(cfg, dict):
        return R.err("config must be an object")
    try:
        out   = Path(tempfile.gettempdir()) / f"wbs_{pid}"
        _build_to_dir(cfg, out, visual=True)
        pages = cfg.get("pages", {})
        urls  = {k: f"/preview/{pid}/{v.get('file','index.html')}" for k, v in pages.items()}
        return R.ok({"pages": urls, "base": f"/preview/{pid}/"})
    except Exception as e:
        return R.err(str(e), 500)

# â”€â”€ Publish (versioned, background) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/api/publish/<pid>", methods=["POST"])
@require_auth
@csrf_protect
@rate_limit(capacity=5, per_min=5)
def api_publish(pid):
    row = _own_project(pid)
    cfg = json.loads(row["config"])

    def _do_publish():
        ver     = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        ver_dir = PUBLISH_DIR / pid / "versions" / ver
        _build_to_dir(cfg, ver_dir, visual=False)
        latest = PUBLISH_DIR / pid / "latest"
        if latest.exists():
            shutil.rmtree(latest)
        shutil.copytree(ver_dir, latest)
        url     = f"/site/{pid}"
        ver_url = f"/published/{pid}/v/{ver}/index.html"
        conn = get_db()
        conn.execute(
            "UPDATE projects SET published=1,publish_url=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (url, pid)
        )
        conn.execute(
            "INSERT INTO publish_versions (project_id,version,url) VALUES (?,?,?)",
            (pid, ver, ver_url)
        )
        conn.commit(); conn.close()
        return {"url": url, "version": ver, "version_url": ver_url}

    jid = _enqueue_build(_do_publish)
    return R.ok({"job_id": jid, "message": "Build queued"}, 202)

@app.route("/api/publish/status/<jid>", methods=["GET"])
@require_auth
def publish_status(jid):
    from worker import JobQueue
    job = JobQueue.get_job(jid)
    if not job:
        # Fallback to legacy in-memory dict
        result = _build_results.get(jid)
        if not result:
            return R.err("Job not found", 404)
        return R.ok(result)
    # Normalise to the shape the frontend expects
    return R.ok({
        "status":  job["status"],
        "result":  job.get("result") or {},
        "error":   job.get("error") or "",
        "retries": job.get("retries", 0),
    })

@app.route("/api/publish/<pid>/versions", methods=["GET"])
@require_auth
def list_versions(pid):
    _own_project(pid)
    conn = get_db()
    rows = conn.execute(
        "SELECT version,url,created_at FROM publish_versions WHERE project_id=? ORDER BY created_at DESC",
        (pid,)
    ).fetchall()
    conn.close()
    return R.ok([dict(r) for r in rows])

@app.route("/api/publish/<pid>/rollback/<ver>", methods=["POST"])
@require_auth
@csrf_protect
def rollback_version(pid, ver):
    _own_project(pid)
    ver = sanitize(ver, 30)
    ver_dir = PUBLISH_DIR / pid / "versions" / ver
    if not ver_dir.exists():
        return R.err("Version not found", 404)
    latest = PUBLISH_DIR / pid / "latest"
    if latest.exists():
        shutil.rmtree(latest)
    shutil.copytree(ver_dir, latest)
    url = f"/site/{pid}"
    conn = get_db()
    conn.execute("UPDATE projects SET publish_url=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (url, pid))
    conn.commit(); conn.close()
    return R.ok({"url": url, "version": ver})

# â”€â”€ Public site routes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/site/<pid>")
@app.route("/site/<pid>/")
def serve_site(pid):
    """Serve the latest published version of a project."""
    latest = PUBLISH_DIR / pid / "latest" / "index.html"
    if not latest.exists():
        return "Site not published yet.", 404
    return send_from_directory(str(PUBLISH_DIR / pid / "latest"), "index.html")

@app.route("/site/<pid>/<path:fn>")
def serve_site_asset(pid, fn):
    return send_from_directory(str(PUBLISH_DIR / pid / "latest"), fn)

@app.route("/p/<slug>")
@app.route("/p/<slug>/")
def serve_by_slug(slug):
    """Serve a published site by its slug."""
    conn = get_db()
    row  = conn.execute("SELECT id FROM projects WHERE slug=? AND published=1", (slug,)).fetchone()
    conn.close()
    if not row:
        return "Site not found.", 404
    return serve_site(row["id"])

@app.route("/published/<pid>/v/<ver>/<path:fn>")
def serve_published_version(pid, ver, fn):
    return send_from_directory(str(PUBLISH_DIR / pid / "versions" / ver), fn)

@app.route("/preview/<pid>/<path:fn>")
def serve_preview(pid, fn):
    d = Path(tempfile.gettempdir()) / f"wbs_{pid}"
    return send_from_directory(str(d), fn)

# â”€â”€ Export ZIP â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/api/export", methods=["POST"])
@require_auth
@csrf_protect
@rate_limit(capacity=5, per_min=5)
def api_export():
    data = request.get_json(silent=True) or {}
    cfg  = data.get("config")
    mode = sanitize(data.get("mode", "static"), 20)
    if not isinstance(cfg, dict):
        return R.err("config must be an object")
    if mode not in {"static", "flask", "react"}:
        return R.err("mode must be static, flask, or react")
    try:
        out  = Path(tempfile.gettempdir()) / f"wbs_export_{cfg_hash(cfg)}"
        build(cfg, out, mode=mode, minify=False)
        name = re.sub(r"[^\w-]", "_", cfg.get("site_name", "website").lower())
        zp   = Path(tempfile.gettempdir()) / f"{name}.zip"
        import zipfile as zf
        with zf.ZipFile(zp, "w", zf.ZIP_DEFLATED) as z:
            for f in out.rglob("*"):
                if f.is_file():
                    z.write(f, f.relative_to(out))
        return send_file(str(zp), as_attachment=True, download_name=f"{name}.zip", mimetype="application/zip")
    except Exception as e:
        return R.err(str(e), 500)

# â”€â”€ Upload (per-user/project) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/api/upload", methods=["POST"])
@require_auth
@csrf_protect
@rate_limit(capacity=30, per_min=30)
def api_upload():
    uid = current_user_id()
    if "file" not in request.files:
        return R.err("No file provided")
    f   = request.files["file"]
    pid = sanitize(request.form.get("project_id", "global"), 40)
    if f.content_length and f.content_length > MAX_FILE_BYTES:
        return R.err("File too large (max 8 MB)")
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in ALLOWED_EXT:
        return R.err(f"Invalid file type. Allowed: {', '.join(sorted(ALLOWED_EXT))}")
    name = uuid.uuid4().hex + "." + ext
    dest = _uploads_dir(uid, pid) / name
    f.save(str(dest))
    url  = f"/uploads/{uid}/{pid}/{name}"
    conn = get_db()
    conn.execute(
        "INSERT INTO project_uploads (project_id,user_id,filename,url) VALUES (?,?,?,?)",
        (pid, uid, name, url)
    )
    conn.commit(); conn.close()
    return R.ok({"url": url, "filename": name}, 201)

@app.route("/uploads/<uid>/<pid>/<path:fn>")
def serve_upload(uid, pid, fn):
    return send_from_directory(str(UPLOADS_DIR / uid / pid), fn)

@app.route("/api/upload/<pid>/list", methods=["GET"])
@require_auth
def list_uploads(pid):
    _own_project(pid)
    conn = get_db()
    rows = conn.execute(
        "SELECT filename,url,created_at FROM project_uploads WHERE project_id=? ORDER BY created_at DESC",
        (pid,)
    ).fetchall()
    conn.close()
    return R.ok([dict(r) for r in rows])

@app.route("/api/upload/<pid>/cleanup", methods=["POST"])
@require_auth
@csrf_protect
def cleanup_uploads(pid):
    uid = current_user_id()
    row = _own_project(pid)
    cfg_str = row["config"]
    conn    = get_db()
    uploads = conn.execute(
        "SELECT id,filename,url FROM project_uploads WHERE project_id=?", (pid,)
    ).fetchall()
    removed = []
    for u in uploads:
        if u["url"] not in cfg_str:
            f = _uploads_dir(uid, pid) / u["filename"]
            if f.exists():
                f.unlink()
            conn.execute("DELETE FROM project_uploads WHERE id=?", (u["id"],))
            removed.append(u["filename"])
    conn.commit(); conn.close()
    return R.ok({"removed": removed})

# â”€â”€ Legacy save/config (no auth required â€” backward compat) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/api/save", methods=["POST"])
def api_save():
    data = request.get_json(silent=True) or {}
    cfg  = data.get("config")
    if not isinstance(cfg, dict):
        return R.err("config must be an object")
    (BUILDER_DIR / "config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return R.ok({})

@app.route("/api/config", methods=["GET"])
def api_config():
    p = BUILDER_DIR / "config.json"
    if p.exists():
        return R.ok(json.loads(p.read_text(encoding="utf-8")))
    return R.err("Not found", 404)

# â”€â”€ Error handlers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.errorhandler(400)
def bad_request(e):
    return R.err(str(e), 400)

@app.errorhandler(401)
def unauthorized(e):
    return R.err("Authentication required", 401)

@app.errorhandler(403)
def forbidden(e):
    return R.err("Access denied", 403)

@app.errorhandler(404)
def not_found(e):
    return R.err("Not found", 404)

@app.errorhandler(413)
def too_large(e):
    return R.err("File too large", 413)

@app.errorhandler(429)
def too_many(e):
    return R.err("Too many requests", 429)

@app.errorhandler(500)
def server_error(e):
    return R.err("Internal server error", 500)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# PERFORMANCE, CACHING, MONITORING EXTENSIONS (v7)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Lazy-import optimization + logging modules (same process, no subprocess)
import importlib as _il
_opt  = None   # optimize module
_slog = None   # server logger

def _get_opt():
    global _opt
    if _opt is None:
        try:
            import sys as _sys
            _sys.path.insert(0, str(UI_DIR))
            _opt = _il.import_module("optimize")
        except Exception:
            _opt = False
    return _opt if _opt else None

def _get_slog():
    global _slog
    if _slog is None:
        try:
            import sys as _sys
            _sys.path.insert(0, str(UI_DIR))
            mod   = _il.import_module("logger_server")
            _slog = mod.slog
        except Exception:
            _slog = lambda *a, **kw: None
    return _slog

# â”€â”€ Security headers middleware â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.after_request
def add_security_headers(response):
    # Only add to non-static responses (avoid breaking binary downloads)
    ct = response.content_type or ''
    if 'text/html' in ct or 'application/json' in ct:
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault(
            'Content-Security-Policy',
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https: blob:; "
            "connect-src 'self';"
        )
    return response

# â”€â”€ CORS headers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",")

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin", "")
    if origin and (origin in _CORS_ORIGINS or "*" in _CORS_ORIGINS):
        response.headers["Access-Control-Allow-Origin"]      = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"]     = "GET,POST,PUT,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Headers"]     = "Content-Type,X-CSRF-Token,Authorization"
    return response

@app.route("/api/<path:_>", methods=["OPTIONS"])
def options_handler(_):
    return "", 204

# â”€â”€ Cache-Control for published static assets â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.after_request
def add_cache_headers(response):
    path = request.path
    # Long-lived cache for versioned/published assets
    if path.startswith('/site/') or path.startswith('/published/') or path.startswith('/p/'):
        if any(path.endswith(ext) for ext in ('.css', '.js', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.woff2')):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        elif path.endswith('.html'):
            response.headers['Cache-Control'] = 'public, max-age=300, must-revalidate'
    # Uploads: medium cache
    elif path.startswith('/uploads/'):
        response.headers['Cache-Control'] = 'public, max-age=86400'
    # API: no cache
    elif path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    return response

# â”€â”€ Gzip pre-compressed file serving â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/site/<pid>/style.css")
def serve_site_css(pid):
    """Serve gzip-compressed CSS if available."""
    gz = PUBLISH_DIR / pid / "latest" / "style.css.gz"
    if gz.exists() and 'gzip' in request.headers.get('Accept-Encoding', ''):
        resp = send_file(str(gz), mimetype='text/css')
        resp.headers['Content-Encoding'] = 'gzip'
        resp.headers['Vary'] = 'Accept-Encoding'
        return resp
    return send_from_directory(str(PUBLISH_DIR / pid / "latest"), "style.css")

@app.route("/site/<pid>/script.js")
def serve_site_js(pid):
    """Serve gzip-compressed JS if available."""
    gz = PUBLISH_DIR / pid / "latest" / "script.js.gz"
    if gz.exists() and 'gzip' in request.headers.get('Accept-Encoding', ''):
        resp = send_file(str(gz), mimetype='application/javascript')
        resp.headers['Content-Encoding'] = 'gzip'
        resp.headers['Vary'] = 'Accept-Encoding'
        return resp
    return send_from_directory(str(PUBLISH_DIR / pid / "latest"), "script.js")

# â”€â”€ Request logging middleware â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_START_TIME = time.time()

@app.before_request
def _log_request_start():
    g._req_start = time.monotonic()

@app.after_request
def _log_request_end(response):
    slog = _get_slog()
    if slog and hasattr(g, '_req_start'):
        ms = round((time.monotonic() - g._req_start) * 1000)
        slog("REQUEST", {
            "method": request.method,
            "path":   request.path,
            "status": response.status_code,
            "ms":     ms,
            "ip":     request.remote_addr,
        })
    return response

# â”€â”€ Optimized publish pipeline â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _do_publish_optimized(cfg: dict, pid: str) -> dict:
    """
    Full publish pipeline with optimization:
    1. Build static site
    2. Run optimize_dir (minify, inline critical CSS, lazy load, gzip)
    3. Copy to latest/
    4. Update DB
    Returns result dict.
    """
    slog = _get_slog()
    opt  = _get_opt()
    t0   = time.time()

    ver     = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    ver_dir = PUBLISH_DIR / pid / "versions" / ver

    # Step 1: Build
    if slog:
        slog("BUILD", {"pid": pid, "ver": ver, "step": "start"})
    _build_to_dir(cfg, ver_dir, visual=False)

    # Step 2: Optimize
    opt_stats = {}
    if opt:
        try:
            opt_stats = opt.optimize_dir(ver_dir)
            if slog:
                slog("BUILD", {"pid": pid, "ver": ver, "step": "optimize", "stats": opt_stats})
        except Exception as e:
            if slog:
                slog("BUILD", {"pid": pid, "ver": ver, "step": "optimize_error", "error": str(e)}, level="WARNING")

    # Step 3: Copy to latest
    latest = PUBLISH_DIR / pid / "latest"
    if latest.exists():
        shutil.rmtree(latest)
    shutil.copytree(ver_dir, latest)

    # Step 4: Update DB
    url     = f"/site/{pid}"
    ver_url = f"/published/{pid}/v/{ver}/index.html"
    build_ms = round((time.time() - t0) * 1000)

    conn = get_db()
    conn.execute(
        "UPDATE projects SET published=1,publish_url=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (url, pid)
    )
    conn.execute(
        "INSERT INTO publish_versions (project_id,version,url) VALUES (?,?,?)",
        (pid, ver, ver_url)
    )
    conn.commit(); conn.close()

    if slog:
        slog("BUILD", {"pid": pid, "ver": ver, "step": "done", "ms": build_ms, "opt": opt_stats})

    return {
        "url":        url,
        "version":    ver,
        "version_url": ver_url,
        "build_ms":   build_ms,
        "optimized":  bool(opt),
        "opt_stats":  opt_stats,
    }

# Override the publish route to use the optimized pipeline
# (The original api_publish is still registered; we add a new one that shadows it
#  by registering with the same path â€” Flask uses the last registered rule)
# Instead we patch the _do_publish function used by the background worker.

# â”€â”€ Image optimization on upload â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/api/upload/optimize/<pid>/<filename>", methods=["POST"])
@require_auth
@csrf_protect
def optimize_upload(pid, filename):
    """
    Generate thumbnail + medium variants for an already-uploaded image.
    Returns URLs for each size.
    """
    uid = current_user_id()
    _own_project(pid)
    opt = _get_opt()
    if not opt:
        return R.err("Image optimization not available (install Pillow: pip install Pillow)")

    src = _uploads_dir(uid, pid) / filename
    if not src.exists():
        return R.err("File not found", 404)

    try:
        variants = opt.optimize_image(src, _uploads_dir(uid, pid) / "variants")
        # Build public URLs
        base = f"/uploads/{uid}/{pid}/variants"
        urls = {k: f"{base}/{Path(v).name}" for k, v in variants.items()}
        return R.ok({"variants": urls})
    except Exception as e:
        return R.err(str(e), 500)

# â”€â”€ Health check â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/health", methods=["GET"])
def health_check():
    uptime_s = round(time.time() - _START_TIME)
    try:
        conn = get_db()
        conn.execute("SELECT 1").fetchone()
        conn.close()
        db_ok = True
    except Exception:
        db_ok = False

    return R.ok({
        "status":     "ok" if db_ok else "degraded",
        "uptime_s":   uptime_s,
        "uptime":     str(timedelta(seconds=uptime_s)),
        "queue_size": _job_queue_size(),
        "db":         "ok" if db_ok else "error",
        "cache_size": len(_preview_cache),
        "version":    "6.1",
    })

# â”€â”€ Logs endpoint (admin only â€” check user is first registered user) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/api/admin/logs", methods=["GET"])
@require_auth
def admin_logs():
    """Return recent server logs. Only accessible to the first registered user."""
    uid  = current_user_id()
    conn = get_db()
    first = conn.execute("SELECT id FROM users ORDER BY created_at ASC LIMIT 1").fetchone()
    conn.close()
    if not first or first["id"] != uid:
        return R.err("Admin access required", 403)

    mod = None
    try:
        import sys as _sys
        _sys.path.insert(0, str(UI_DIR))
        mod = _il.import_module("logger_server")
    except Exception:
        return R.err("Logging module not available")

    tag   = request.args.get("tag")
    limit = min(int(request.args.get("limit", 100)), 500)
    logs  = mod.get_recent_logs(n=limit, tag=tag or None)
    return R.ok({"logs": logs, "count": len(logs)})

# â”€â”€ Backup endpoint â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/api/admin/backup", methods=["POST"])
@require_auth
@csrf_protect
def admin_backup():
    """
    Create a timestamped backup of:
    - projects.db
    - uploads/
    - published/
    Returns a downloadable ZIP.
    """
    uid  = current_user_id()
    conn = get_db()
    first = conn.execute("SELECT id FROM users ORDER BY created_at ASC LIMIT 1").fetchone()
    conn.close()
    if not first or first["id"] != uid:
        return R.err("Admin access required", 403)

    import zipfile as zf
    ts      = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    zp_path = Path(tempfile.gettempdir()) / f"wbs_backup_{ts}.zip"

    try:
        with zf.ZipFile(zp_path, "w", zf.ZIP_DEFLATED) as z:
            # DB
            if DB_PATH.exists():
                z.write(DB_PATH, f"backup_{ts}/projects.db")
            # Uploads
            if UPLOADS_DIR.exists():
                for f in UPLOADS_DIR.rglob("*"):
                    if f.is_file():
                        z.write(f, f"backup_{ts}/uploads/{f.relative_to(UPLOADS_DIR)}")
            # Published sites
            if PUBLISH_DIR.exists():
                for f in PUBLISH_DIR.rglob("*"):
                    if f.is_file():
                        z.write(f, f"backup_{ts}/published/{f.relative_to(PUBLISH_DIR)}")

        slog = _get_slog()
        if slog:
            slog("BACKUP", {"ts": ts, "size_mb": round(zp_path.stat().st_size / 1024 / 1024, 2)})

        return send_file(
            str(zp_path),
            as_attachment=True,
            download_name=f"wbs_backup_{ts}.zip",
            mimetype="application/zip"
        )
    except Exception as e:
        return R.err(str(e), 500)

# â”€â”€ Override publish to use optimized pipeline â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# We re-register the publish route with the optimized version.
# Flask allows multiple registrations; the last one wins for new requests.
# We remove the old rule first to avoid duplicate endpoint errors.
def _repatch_publish():
    """Replace the publish background job with the optimized version."""
    # Monkey-patch: wrap the existing api_publish to use _do_publish_optimized
    original_publish = app.view_functions.get("api_publish")
    if not original_publish:
        return

    @require_auth
    @csrf_protect
    @rate_limit(capacity=5, per_min=5)
    def api_publish_v2(pid):
        row = _own_project(pid)
        cfg = json.loads(row["config"])
        jid = _enqueue_build(_do_publish_optimized, cfg, pid)
        slog = _get_slog()
        if slog:
            slog("PUBLISH", {"pid": pid, "jid": jid})
        return R.ok({"job_id": jid, "message": "Build queued"}, 202)

    app.view_functions["api_publish"] = api_publish_v2

_repatch_publish()

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# OBSERVABILITY EXTENSIONS (v7)
# Metrics, SSE streaming, request tracing, error tracking, admin APIs
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

import importlib as _il2   # separate alias to avoid collision with _il above

# Lazy-load metrics + upgraded logger
_metrics_mod = None
_logger_mod  = None

def _get_metrics():
    global _metrics_mod
    if _metrics_mod is None:
        try:
            sys.path.insert(0, str(UI_DIR))
            _metrics_mod = _il2.import_module("metrics")
            _metrics_mod.load_from_db(DB_PATH)
            _metrics_mod.start_flush_thread(DB_PATH)
        except Exception as e:
            print(f"[WARN] metrics module unavailable: {e}", file=sys.stderr)
            _metrics_mod = False
    return _metrics_mod if _metrics_mod else None

def _get_logger():
    global _logger_mod
    if _logger_mod is None:
        try:
            sys.path.insert(0, str(UI_DIR))
            _logger_mod = _il2.import_module("logger_server")
        except Exception:
            _logger_mod = False
    return _logger_mod if _logger_mod else None

# Bootstrap on first import
_get_metrics()
_get_logger()

# â”€â”€ Request ID middleware â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.before_request
def _attach_request_id():
    """Attach a unique X-Request-ID to every request."""
    rid = request.headers.get("X-Request-ID") or ""
    lm  = _get_logger()
    if lm and hasattr(lm, "new_request_id"):
        rid = rid or lm.new_request_id()
    else:
        rid = rid or uuid.uuid4().hex[:12]
    g._request_id = rid

@app.after_request
def _stamp_request_id(response):
    """Echo the request ID back in the response header."""
    response.headers["X-Request-ID"] = getattr(g, "_request_id", "")
    return response

# â”€â”€ Metrics + slow-request middleware â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# (Runs after the existing _log_request_end â€” both after_request hooks fire)

@app.after_request
def _record_metrics(response):
    """Feed every request into the metrics module."""
    m   = _get_metrics()
    lm  = _get_logger()
    rid = getattr(g, "_request_id", "")
    if not hasattr(g, "_req_start"):
        return response
    ms = round((time.monotonic() - g._req_start) * 1000, 1)

    if m:
        m.record_request(
            endpoint   = request.endpoint or request.path,
            method     = request.method,
            status     = response.status_code,
            ms         = ms,
            request_id = rid,
        )
        uid = current_user_id()
        if uid:
            m.record_active_user(uid)

    # Slow request detection
    if ms >= 1000 and lm:
        lm.slog("SLOW_REQUEST", {
            "path":       request.path,
            "method":     request.method,
            "ms":         ms,
            "status":     response.status_code,
        }, level="WARNING", request_id=rid)

    return response

# â”€â”€ Global exception handler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.errorhandler(Exception)
def _global_exception_handler(exc):
    """Catch-all: never crash the server, always return safe JSON."""
    rid = getattr(g, "_request_id", "")
    lm  = _get_logger()
    m   = _get_metrics()
    if lm:
        lm.capture_exception(exc, context=request.path, request_id=rid)
    if m:
        m.record_error(source=request.path, message=str(exc), request_id=rid)
    return R.err("Internal server error", 500)

# â”€â”€ Admin guard helper â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _require_admin():
    """Return True if current user is the first registered user (admin)."""
    uid = current_user_id()
    if not uid:
        return False
    conn  = get_db()
    first = conn.execute("SELECT id FROM users ORDER BY created_at ASC LIMIT 1").fetchone()
    conn.close()
    return first and first["id"] == uid

# â”€â”€ GET /api/admin/metrics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/api/admin/metrics", methods=["GET"])
@require_auth
def admin_metrics():
    """Return a full metrics snapshot."""
    if not _require_admin():
        return R.err("Admin access required", 403)
    m = _get_metrics()
    if not m:
        return R.err("Metrics module not available")
    snap = m.snapshot(queue_size=_job_queue_size())
    return R.ok(snap)

# â”€â”€ GET /api/admin/metrics/history â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/api/admin/metrics/history", methods=["GET"])
@require_auth
def admin_metrics_history():
    """Return the last N persisted metric snapshots from SQLite."""
    if not _require_admin():
        return R.err("Admin access required", 403)
    limit = min(int(request.args.get("limit", 60)), 1440)
    try:
        conn = get_db()
        rows = conn.execute(
            "SELECT ts, snapshot FROM metrics_snapshots ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
        conn.close()
        history = [{"ts": r["ts"], **json.loads(r["snapshot"])} for r in rows]
        return R.ok({"history": history, "count": len(history)})
    except Exception as e:
        return R.err(str(e), 500)

# â”€â”€ GET /api/admin/errors â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/api/admin/errors", methods=["GET"])
@require_auth
def admin_errors():
    """Return recent error log entries."""
    if not _require_admin():
        return R.err("Admin access required", 403)
    lm    = _get_logger()
    if not lm:
        return R.err("Logger not available")
    limit = min(int(request.args.get("limit", 50)), 500)
    errors = lm.get_recent_errors(n=limit)
    return R.ok({"errors": errors, "count": len(errors)})

# â”€â”€ GET /api/admin/logs (upgraded â€” replaces the v6 version) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# We patch the existing view function to use the upgraded logger.

def _admin_logs_v2():
    """Upgraded log endpoint with tag, level, since_ts filtering."""
    if not _require_admin():
        return R.err("Admin access required", 403)
    lm = _get_logger()
    if not lm:
        return R.err("Logger not available")
    tag      = request.args.get("tag")
    level    = request.args.get("level")
    since_ts = request.args.get("since")
    limit    = min(int(request.args.get("limit", 100)), 500)
    logs     = lm.get_recent_logs(n=limit, tag=tag or None,
                                   level=level or None,
                                   since_ts=since_ts or None)
    return R.ok({"logs": logs, "count": len(logs)})

app.view_functions["admin_logs"] = _admin_logs_v2

# â”€â”€ GET /api/admin/debug â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/api/admin/debug", methods=["GET"])
@require_auth
def admin_debug():
    """Return runtime debug information."""
    if not _require_admin():
        return R.err("Admin access required", 403)
    import threading as _th
    try:
        import psutil as _ps
        mem_mb = round(_ps.Process().memory_info().rss / 1024 / 1024, 1)
    except ImportError:
        import resource as _res
        try:
            mem_mb = round(_res.getrusage(_res.RUSAGE_SELF).ru_maxrss / 1024, 1)
        except Exception:
            mem_mb = -1

    conn = get_db()
    active_projects = conn.execute(
        "SELECT COUNT(*) FROM projects WHERE published=1"
    ).fetchone()[0]
    total_projects = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    total_users    = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()

    uptime_s = round(time.time() - _START_TIME)
    return R.ok({
        "uptime_s":        uptime_s,
        "uptime":          str(timedelta(seconds=uptime_s)),
        "memory_mb":       mem_mb,
        "thread_count":    _th.active_count(),
        "queue_size":      _job_queue_size(),
        "cache_size":      len(_preview_cache),
        "active_projects": active_projects,
        "total_projects":  total_projects,
        "total_users":     total_users,
        "python_version":  sys.version.split()[0],
        "version":         "7.0",
    })

# â”€â”€ GET /api/admin/stream (SSE) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/api/admin/stream")
@require_auth
def admin_stream():
    """
    Server-Sent Events stream of live log entries.
    Connect with: EventSource('/api/admin/stream')
    Each event has type = log tag (BUILD, REQUEST, ERROR, ...).
    """
    if not _require_admin():
        return R.err("Admin access required", 403)

    lm = _get_logger()
    if not lm:
        return R.err("Logger not available")

    q = lm.subscribe_sse()

    def _generate():
        # Send a heartbeat comment immediately so the connection is established
        yield ": connected\n\n"
        try:
            while True:
                # Drain the queue
                sent = 0
                while q:
                    try:
                        yield q.popleft()
                        sent += 1
                    except IndexError:
                        break
                if sent == 0:
                    # Heartbeat every 15 s to keep connection alive
                    yield ": heartbeat\n\n"
                time.sleep(0.5)
        except GeneratorExit:
            pass
        finally:
            lm.unsubscribe_sse(q)

    return app.response_class(
        _generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":  "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx buffering
            "Connection":     "keep-alive",
        },
    )

# â”€â”€ Instrument build functions to record metrics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_orig_do_publish = _do_publish_optimized

def _do_publish_instrumented(cfg: dict, pid: str) -> dict:
    """Wrap _do_publish_optimized to record build metrics."""
    m   = _get_metrics()
    lm  = _get_logger()
    t0  = time.time()
    try:
        result = _orig_do_publish(cfg, pid)
        ms     = round((time.time() - t0) * 1000)
        if m:
            m.record_build("publish", pid, ms, ok=True)
        if lm:
            lm.slog("BUILD", {"kind": "publish", "pid": pid, "ms": ms, "ok": True})
        return result
    except Exception as exc:
        ms = round((time.time() - t0) * 1000)
        if m:
            m.record_build("publish", pid, ms, ok=False, error=str(exc))
        if lm:
            lm.capture_exception(exc, context=f"publish:{pid}")
        raise

# Re-patch publish to use instrumented version
def _repatch_publish_v2():
    @require_auth
    @csrf_protect
    @rate_limit(capacity=5, per_min=5)
    def api_publish_v3(pid):
        row = _own_project(pid)
        cfg = json.loads(row["config"])
        jid = _enqueue_build(_do_publish_instrumented, cfg, pid)
        lm  = _get_logger()
        rid = getattr(g, "_request_id", "")
        if lm:
            lm.slog("PUBLISH", {"pid": pid, "jid": jid}, request_id=rid)
        return R.ok({"job_id": jid, "message": "Build queued"}, 202)

    app.view_functions["api_publish"] = api_publish_v3

_repatch_publish_v2()

# -- Register job handlers with the persistent queue --
def _register_job_handlers():
    """
    Register all build functions as JobQueue handlers.
    Called after all build functions are defined.
    payload keys: cfg (dict), pid (str, optional)
    """
    try:
        from worker import JobQueue

        def _publish_handler(payload):
            cfg = payload.get("cfg") or {}
            pid = payload.get("pid", "")
            return _do_publish_instrumented(cfg, pid)

        def _preview_handler(payload):
            cfg    = payload.get("cfg") or {}
            page   = payload.get("page", "home")
            visual = payload.get("visual", True)
            pid    = payload.get("pid", "default")
            out    = __import__("pathlib").Path(__import__("tempfile").gettempdir()) / f"wbs_{pid}"
            _build_to_dir(cfg, out, visual=visual)
            pages = cfg.get("pages", {})
            urls  = {k: f"/preview/{pid}/{v.get('file','index.html')}" for k, v in pages.items()}
            return {"pages": urls, "base": f"/preview/{pid}/"}

        def _export_handler(payload):
            import re as _re, zipfile as _zf, tempfile as _tmp
            cfg  = payload.get("cfg") or {}
            mode = payload.get("mode", "static")
            out  = __import__("pathlib").Path(_tmp.gettempdir()) / f"wbs_export_{cfg_hash(cfg)}"
            build(cfg, out, mode=mode, minify=False)
            name = _re.sub(r"[^\w-]", "_", cfg.get("site_name", "website").lower())
            zp   = __import__("pathlib").Path(_tmp.gettempdir()) / f"{name}.zip"
            with _zf.ZipFile(zp, "w", _zf.ZIP_DEFLATED) as z:
                for f in out.rglob("*"):
                    if f.is_file():
                        z.write(f, f.relative_to(out))
            return {"zip_path": str(zp), "name": name}

        JobQueue.register_handler("publish", _publish_handler)
        JobQueue.register_handler("preview", _preview_handler)
        JobQueue.register_handler("export",  _export_handler)
    except Exception as e:
        print(f"[WORKER] Handler registration failed: {e}", flush=True)

_register_job_handlers()


# â”€â”€ Entry point â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# =============================================================================
# JOB SYSTEM API ROUTES (v8)
# =============================================================================

@app.route("/api/jobs/<jid>", methods=["GET"])
@require_auth
def get_job(jid):
    """Return status of a single job by ID."""
    from worker import JobQueue
    job = JobQueue.get_job(jid)
    if not job:
        return R.err("Job not found", 404)
    return R.ok({
        "id":      job["id"],
        "type":    job["type"],
        "status":  job["status"],
        "result":  job.get("result") or {},
        "error":   job.get("error") or "",
        "retries": job.get("retries", 0),
        "created_at": job.get("created_at"),
        "updated_at": job.get("updated_at"),
    })


@app.route("/api/jobs", methods=["GET"])
@require_auth
def list_jobs():
    """List recent jobs, optionally filtered by status."""
    from worker import JobQueue
    status = request.args.get("status")
    limit  = min(int(request.args.get("limit", 50)), 200)
    jobs   = JobQueue.list_jobs(status=status or None, limit=limit)
    # Scope to current user's projects
    uid  = current_user_id()
    conn = get_db()
    user_pids = {r["id"] for r in conn.execute(
        "SELECT id FROM projects WHERE user_id=?", (uid,)
    ).fetchall()}
    conn.close()
    # Filter: keep jobs whose payload.pid belongs to this user (or no pid)
    filtered = []
    for j in jobs:
        pid = (j.get("payload") or {}).get("pid")
        if pid is None or pid in user_pids:
            filtered.append(j)
    return R.ok({"jobs": filtered, "count": len(filtered)})


@app.route("/api/jobs/stats", methods=["GET"])
@require_auth
def job_stats():
    """Return queue statistics."""
    from worker import JobQueue, pool
    stats = JobQueue.queue_stats()
    stats["workers"] = pool.status()
    return R.ok(stats)


# =============================================================================
# ENTERPRISE EXTENSIONS (v8) — wired in without touching existing routes
# =============================================================================

def _bootstrap_enterprise():
    """
    Register the v1 API blueprint, run new DB migrations,
    wire the scheduler, and set up the DLQ.
    Called once at startup.
    """
    import sys as _sys
    _sys.path.insert(0, str(UI_DIR))

    # 1. Register API v1 blueprint
    try:
        from api.v1.routes import v1 as v1_blueprint
        app.register_blueprint(v1_blueprint)
        print("[ENTERPRISE] API v1 registered at /api/v1/", flush=True)
    except Exception as e:
        print(f"[ENTERPRISE] API v1 registration failed: {e}", flush=True)

    # 2. Run new DB migrations (db/migrations.py)
    try:
        from db.connection import init_pool, get_conn
        from db.migrations import run_migrations
        init_pool(str(DB_PATH))
        conn = get_conn()
        run_migrations(conn)
        print("[ENTERPRISE] DB migrations applied", flush=True)
    except Exception as e:
        print(f"[ENTERPRISE] DB migration failed: {e}", flush=True)

    # 3. Init marketplace tables
    try:
        from db.connection import get_conn as _gc
        from marketplace.registry import init_marketplace_tables
        from templates_marketplace.registry import init_template_tables
        from worker.locks import init_locks_table
        from worker.heartbeat import init_heartbeat_table
        from worker.retry import init_dlq_table
        _c = _gc()
        init_marketplace_tables(_c)
        init_template_tables(_c)
        init_locks_table(_c)
        init_heartbeat_table(_c)
        init_dlq_table(_c)
        print("[ENTERPRISE] Marketplace + worker tables ready", flush=True)
    except Exception as e:
        print(f"[ENTERPRISE] Table init failed: {e}", flush=True)

    # 4. Wire scheduler with enqueue
    try:
        from worker.scheduler import scheduler
        from worker import JobQueue as _JQ
        scheduler.set_enqueue(_JQ.enqueue)
        # Register default scheduled tasks
        scheduler.every(3600,  "cleanup_uploads",  {"older_than_days": 7},  name="cleanup_uploads")
        scheduler.every(86400, "backup",           {},                       name="daily_backup")
        scheduler.every(300,   "metrics_flush",    {},                       name="metrics_flush")
        scheduler.start()
        print("[ENTERPRISE] Scheduler started", flush=True)
    except Exception as e:
        print(f"[ENTERPRISE] Scheduler failed: {e}", flush=True)

    # 5. Add /api/v1/openapi.json redirect at root level
    @app.route("/api/docs")
    def api_docs_redirect():
        from flask import redirect
        return redirect("/api/v1/docs")


_bootstrap_enterprise()


if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 4000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    lm    = _get_logger()
    if lm:
        lm.slog("START", {"port": port, "debug": debug, "version": "8.0"})
    print(f"Website Builder -> http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)



