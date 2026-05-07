"""
gunicorn.conf.py — Production Gunicorn configuration.
Run: gunicorn -c gunicorn.conf.py server:app
"""
import multiprocessing, os

# ── Binding ───────────────────────────────────────────────────────────────────
bind = f"0.0.0.0:{os.environ.get('PORT', '4000')}"

# ── Workers ───────────────────────────────────────────────────────────────────
# Use gevent for async I/O (better for SSE + long-poll).
# Falls back to sync if gevent is not installed.
try:
    import gevent  # noqa: F401
    worker_class = "gevent"
    worker_connections = 1000
except ImportError:
    worker_class = "sync"
    worker_connections = None

_cpu = multiprocessing.cpu_count()
workers = int(os.environ.get("GUNICORN_WORKERS", min(4, _cpu * 2 + 1)))

# ── Timeouts ──────────────────────────────────────────────────────────────────
timeout         = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
graceful_timeout = 30
keepalive       = 5

# ── Request cycling (memory leak guard) ──────────────────────────────────────
max_requests        = 1000
max_requests_jitter = 100

# ── Logging ───────────────────────────────────────────────────────────────────
accesslog = "-"   # stdout → captured by Docker
errorlog  = "-"   # stderr → captured by Docker
loglevel  = os.environ.get("LOG_LEVEL", "info")

# ── Security ──────────────────────────────────────────────────────────────────
# Forward real client IP from nginx
forwarded_allow_ips = "*"
proxy_protocol      = False

# ── Performance ───────────────────────────────────────────────────────────────
preload_app = True   # load app once before forking (saves memory)
