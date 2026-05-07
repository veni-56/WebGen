"""
metrics.py — In-process metrics collection for the Website Builder.

Design:
  - All storage is in-memory (thread-safe deques / counters).
  - A rolling 1-hour window is kept for time-series data.
  - A SQLite flush happens every 60 s so metrics survive restarts.
  - No external dependencies.

Public API:
  record_request(endpoint, method, status, ms, request_id)
  record_build(kind, pid, ms, ok, error)
  record_error(source, message, request_id)
  record_active_user(user_id)
  snapshot()          -> dict  (current metrics snapshot)
  flush_to_db(db_path) -> None (persist to SQLite)
  load_from_db(db_path) -> None (restore counters on startup)
"""
import collections, json, sqlite3, threading, time
from datetime import datetime, timezone
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
WINDOW_SECONDS  = 3600          # 1-hour rolling window
MAX_SERIES_LEN  = 720           # max data points per series (1 per 5 s)
FLUSH_INTERVAL  = 60            # seconds between SQLite flushes
SLOW_MS         = 1000          # threshold for slow-request alert
ERROR_RATE_WARN = 10            # errors/min that triggers an alert
QUEUE_WARN      = 15            # queue depth that triggers an alert

# ─────────────────────────────────────────────────────────────────────────────
# Thread-safe primitives
# ─────────────────────────────────────────────────────────────────────────────
_lock = threading.Lock()

# Rolling time-series: deque of (timestamp_float, value)
_req_latency:   collections.deque = collections.deque(maxlen=MAX_SERIES_LEN)
_build_times:   collections.deque = collections.deque(maxlen=MAX_SERIES_LEN)
_error_series:  collections.deque = collections.deque(maxlen=MAX_SERIES_LEN)
_queue_series:  collections.deque = collections.deque(maxlen=MAX_SERIES_LEN)

# Per-endpoint latency accumulator: {endpoint: [ms, ...]}
_endpoint_stats: dict[str, list] = collections.defaultdict(list)

# Counters (lifetime, reset on restart unless loaded from DB)
_counters: dict[str, int] = {
    "requests_total":  0,
    "requests_2xx":    0,
    "requests_4xx":    0,
    "requests_5xx":    0,
    "builds_total":    0,
    "builds_ok":       0,
    "builds_failed":   0,
    "errors_total":    0,
    "slow_requests":   0,
}

# Active users: {user_id: last_seen_timestamp}
_active_users: dict[str, float] = {}
_ACTIVE_WINDOW = 300   # 5 minutes = "online"

# Alert callbacks: list of callables(alert_type, data)
_alert_handlers: list = []

# ─────────────────────────────────────────────────────────────────────────────
# Public recording functions
# ─────────────────────────────────────────────────────────────────────────────

def record_request(endpoint: str, method: str, status: int, ms: float,
                   request_id: str = "") -> None:
    """Record a completed HTTP request."""
    now = time.time()
    with _lock:
        _counters["requests_total"] += 1
        if 200 <= status < 300:
            _counters["requests_2xx"] += 1
        elif 400 <= status < 500:
            _counters["requests_4xx"] += 1
        elif status >= 500:
            _counters["requests_5xx"] += 1

        _req_latency.append((now, ms))
        _endpoint_stats[endpoint].append(ms)
        # Keep per-endpoint list bounded
        if len(_endpoint_stats[endpoint]) > 200:
            _endpoint_stats[endpoint] = _endpoint_stats[endpoint][-200:]

        if ms >= SLOW_MS:
            _counters["slow_requests"] += 1
            _fire_alert("SLOW_REQUEST", {
                "endpoint": endpoint, "method": method,
                "ms": ms, "request_id": request_id
            })


def record_build(kind: str, pid: str, ms: float, ok: bool,
                 error: str = "") -> None:
    """Record a build (publish or preview)."""
    now = time.time()
    with _lock:
        _counters["builds_total"] += 1
        if ok:
            _counters["builds_ok"] += 1
        else:
            _counters["builds_failed"] += 1
            _fire_alert("BUILD_FAILED", {"kind": kind, "pid": pid, "error": error})
        _build_times.append((now, ms))


def record_error(source: str, message: str, request_id: str = "") -> None:
    """Record an application error."""
    now = time.time()
    with _lock:
        _counters["errors_total"] += 1
        _error_series.append((now, 1))
        # Check error rate (last 60 s)
        cutoff = now - 60
        recent = sum(1 for ts, _ in _error_series if ts >= cutoff)
        if recent >= ERROR_RATE_WARN:
            _fire_alert("HIGH_ERROR_RATE", {
                "errors_per_min": recent,
                "threshold": ERROR_RATE_WARN,
                "source": source,
            })


def record_active_user(user_id: str) -> None:
    """Mark a user as recently active."""
    with _lock:
        _active_users[user_id] = time.time()


def record_queue_size(size: int) -> None:
    """Record current build queue depth."""
    now = time.time()
    with _lock:
        _queue_series.append((now, size))
        if size >= QUEUE_WARN:
            _fire_alert("QUEUE_FULL", {"queue_size": size, "threshold": QUEUE_WARN})


# ─────────────────────────────────────────────────────────────────────────────
# Snapshot
# ─────────────────────────────────────────────────────────────────────────────

def snapshot(queue_size: int = 0) -> dict:
    """Return a complete metrics snapshot dict."""
    now = time.time()
    cutoff_1h  = now - WINDOW_SECONDS
    cutoff_5m  = now - 300
    cutoff_1m  = now - 60

    with _lock:
        # Prune stale active users
        stale = [uid for uid, ts in _active_users.items() if now - ts > _ACTIVE_WINDOW]
        for uid in stale:
            del _active_users[uid]
        users_online = len(_active_users)

        # Latency stats (last 1 h)
        recent_lat = [ms for ts, ms in _req_latency if ts >= cutoff_1h]
        lat_stats  = _percentiles(recent_lat)

        # Per-endpoint p95
        ep_stats = {}
        for ep, times in _endpoint_stats.items():
            ep_stats[ep] = _percentiles(times[-100:])

        # Build stats (last 1 h)
        recent_builds = [(ts, ms) for ts, ms in _build_times if ts >= cutoff_1h]
        build_ms_list = [ms for _, ms in recent_builds]

        # Error rate
        errors_1m = sum(1 for ts, _ in _error_series if ts >= cutoff_1m)
        errors_5m = sum(1 for ts, _ in _error_series if ts >= cutoff_5m)

        # Queue history (last 5 min)
        q_hist = [(ts, v) for ts, v in _queue_series if ts >= cutoff_5m]

        counters_copy = dict(_counters)

    record_queue_size(queue_size)

    return {
        "timestamp":    datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "counters":     counters_copy,
        "api_latency": {
            "overall":     lat_stats,
            "by_endpoint": ep_stats,
        },
        "builds": {
            "total_1h":   len(recent_builds),
            "avg_ms":     round(sum(build_ms_list) / len(build_ms_list), 1) if build_ms_list else 0,
            "max_ms":     max(build_ms_list, default=0),
            "ok":         counters_copy["builds_ok"],
            "failed":     counters_copy["builds_failed"],
        },
        "errors": {
            "total":      counters_copy["errors_total"],
            "per_min":    errors_1m,
            "per_5min":   errors_5m,
        },
        "users_online": users_online,
        "queue": {
            "current":    queue_size,
            "history_5m": [(round(ts - time.time()), v) for ts, v in q_hist],
        },
    }


def _percentiles(values: list) -> dict:
    if not values:
        return {"count": 0, "avg": 0, "p50": 0, "p95": 0, "p99": 0, "max": 0}
    s = sorted(values)
    n = len(s)
    def p(pct): return s[min(int(n * pct / 100), n - 1)]
    return {
        "count": n,
        "avg":   round(sum(s) / n, 1),
        "p50":   round(p(50), 1),
        "p95":   round(p(95), 1),
        "p99":   round(p(99), 1),
        "max":   round(max(s), 1),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Alert system
# ─────────────────────────────────────────────────────────────────────────────

def add_alert_handler(fn) -> None:
    """Register a callable(alert_type: str, data: dict) for alerts."""
    _alert_handlers.append(fn)


def _fire_alert(alert_type: str, data: dict) -> None:
    """Internal: fire all registered alert handlers (called under _lock)."""
    import sys
    print(f"\033[33m[ALERT:{alert_type}] {json.dumps(data)}\033[0m", file=sys.stderr)
    for fn in _alert_handlers:
        try:
            fn(alert_type, data)
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# SQLite persistence
# ─────────────────────────────────────────────────────────────────────────────

def flush_to_db(db_path: str | Path) -> None:
    """Persist current counters to SQLite metrics table."""
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics_snapshots (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                ts         TEXT NOT NULL,
                snapshot   TEXT NOT NULL
            )
        """)
        # Keep only last 1440 snapshots (24 h at 1/min)
        conn.execute("""
            DELETE FROM metrics_snapshots
            WHERE id NOT IN (
                SELECT id FROM metrics_snapshots ORDER BY id DESC LIMIT 1440
            )
        """)
        conn.execute(
            "INSERT INTO metrics_snapshots (ts, snapshot) VALUES (?, ?)",
            (datetime.now(timezone.utc).isoformat(), json.dumps(snapshot()))
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def load_from_db(db_path: str | Path) -> None:
    """Restore counters from the most recent DB snapshot."""
    try:
        conn = sqlite3.connect(str(db_path))
        row  = conn.execute(
            "SELECT snapshot FROM metrics_snapshots ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if not row:
            return
        data = json.loads(row[0])
        with _lock:
            for k, v in data.get("counters", {}).items():
                if k in _counters:
                    _counters[k] = v
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Background flush thread
# ─────────────────────────────────────────────────────────────────────────────

def start_flush_thread(db_path: str | Path) -> None:
    """Start a daemon thread that flushes metrics to SQLite every 60 s."""
    def _loop():
        while True:
            time.sleep(FLUSH_INTERVAL)
            flush_to_db(db_path)

    t = threading.Thread(target=_loop, daemon=True, name="metrics-flush")
    t.start()
