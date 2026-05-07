"""
gunicorn.conf.py — Production Gunicorn config (Render.com compatible)
Run: gunicorn -c gunicorn.conf.py server:app
"""
import multiprocessing, os

# Render sets PORT automatically; fallback to 4000 for local dev
bind = f"0.0.0.0:{os.environ.get('PORT', '4000')}"

# Workers
try:
    import gevent
    worker_class       = "gevent"
    worker_connections = 1000
except ImportError:
    worker_class       = "sync"
    worker_connections = None

_cpu     = multiprocessing.cpu_count()
workers  = int(os.environ.get("GUNICORN_WORKERS", min(4, _cpu * 2 + 1)))

# Timeouts — allow slow builds
timeout          = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
graceful_timeout = 30
keepalive        = 5

# Memory leak guard
max_requests        = 1000
max_requests_jitter = 100

# Logging — stdout/stderr so Render captures it
accesslog = "-"
errorlog  = "-"
loglevel  = os.environ.get("LOG_LEVEL", "info")

# Trust Render's proxy
forwarded_allow_ips = "*"
proxy_protocol      = False

# Load app once before forking
preload_app = True
