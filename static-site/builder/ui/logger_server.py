"""
logger_server.py v2 — Structured server-side logging + SSE event bus.

New in v2:
  - Separate errors.log file
  - SSE event queue for /api/admin/stream
  - Request ID support (X-Request-ID)
  - Log filtering by tag, level, time range
  - Global exception capture helper

Public API:
  slog(tag, data, level, request_id)
  get_recent_logs(n, tag, level, since_ts)
  get_recent_errors(n)
  subscribe_sse()   -> generator that yields SSE-formatted strings
  unsubscribe_sse(q)
  capture_exception(exc, context, request_id)
"""
import collections, json, logging, os, sys, threading, traceback, uuid
from datetime import datetime, timezone
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
_LOG_DIR    = Path(os.environ.get("LOG_DIR", str(Path(__file__).parent / "logs")))
_LOG_FILE   = _LOG_DIR / "server.log"
_ERR_FILE   = _LOG_DIR / "errors.log"
_LOG_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────
_MAX_BYTES      = 10 * 1024 * 1024   # 10 MB before rotation
_SSE_QUEUE_MAX  = 200                # max events per SSE subscriber
_SSE_KEEP_LAST  = 500                # in-memory ring buffer for late subscribers

# ─────────────────────────────────────────────────────────────────────────────
# Thread primitives
# ─────────────────────────────────────────────────────────────────────────────
_lock         = threading.Lock()
_sse_lock     = threading.Lock()
_subscribers: list[collections.deque] = []   # one deque per SSE client
_recent_ring: collections.deque = collections.deque(maxlen=_SSE_KEEP_LAST)

# ─────────────────────────────────────────────────────────────────────────────
# Stdlib stderr logger
# ─────────────────────────────────────────────────────────────────────────────
_stderr_log = logging.getLogger("wbs")
if not _stderr_log.handlers:
    _h = logging.StreamHandler(sys.stderr)
    _h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    _stderr_log.addHandler(_h)
    _stderr_log.setLevel(logging.INFO)


# ─────────────────────────────────────────────────────────────────────────────
# Core logging function
# ─────────────────────────────────────────────────────────────────────────────

def slog(tag: str, data: dict | None = None, level: str = "INFO",
         request_id: str = "") -> None:
    """
    Write a structured log entry to server.log (and errors.log for ERROR level).

    tag:        uppercase label — REQUEST, BUILD, AUTH, UPLOAD, ERROR, ALERT, ...
    data:       JSON-serialisable dict
    level:      INFO | WARNING | ERROR
    request_id: optional X-Request-ID for tracing
    """
    entry = {
        "ts":         datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "tag":        tag,
        "level":      level,
        "request_id": request_id or "",
        "data":       data or {},
    }
    line = json.dumps(entry, separators=(",", ":"))

    with _lock:
        _rotate_if_needed(_LOG_FILE)
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")

        if level == "ERROR":
            _rotate_if_needed(_ERR_FILE)
            with open(_ERR_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")

    # Push to SSE ring + all live subscribers
    _push_sse(entry)

    # Mirror to stderr
    msg = f"[{tag}] {json.dumps(data or {}, separators=(',', ':'))}"
    if request_id:
        msg = f"[{request_id[:8]}] {msg}"
    if level == "ERROR":
        _stderr_log.error(msg)
    elif level == "WARNING":
        _stderr_log.warning(msg)
    else:
        _stderr_log.info(msg)


def _rotate_if_needed(path: Path) -> None:
    """Rotate log file if it exceeds _MAX_BYTES. Called under _lock."""
    if path.exists() and path.stat().st_size > _MAX_BYTES:
        ts      = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        rotated = path.with_suffix(f".{ts}.log")
        path.rename(rotated)


# ─────────────────────────────────────────────────────────────────────────────
# Exception capture
# ─────────────────────────────────────────────────────────────────────────────

def capture_exception(exc: Exception, context: str = "",
                      request_id: str = "") -> None:
    """Log an exception with full traceback to errors.log."""
    tb = traceback.format_exc()
    slog("EXCEPTION", {
        "context":   context,
        "type":      type(exc).__name__,
        "message":   str(exc),
        "traceback": tb,
    }, level="ERROR", request_id=request_id)


# ─────────────────────────────────────────────────────────────────────────────
# Log retrieval
# ─────────────────────────────────────────────────────────────────────────────

def get_recent_logs(n: int = 100, tag: str | None = None,
                    level: str | None = None,
                    since_ts: str | None = None) -> list[dict]:
    """
    Return the last n log entries from server.log.
    Optionally filter by tag, level, or ISO timestamp (since_ts).
    """
    return _read_log_file(_LOG_FILE, n, tag, level, since_ts)


def get_recent_errors(n: int = 100) -> list[dict]:
    """Return the last n entries from errors.log."""
    return _read_log_file(_ERR_FILE, n)


def _read_log_file(path: Path, n: int, tag: str | None = None,
                   level: str | None = None,
                   since_ts: str | None = None) -> list[dict]:
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []

    entries = []
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        if tag   and e.get("tag")   != tag:
            continue
        if level and e.get("level") != level:
            continue
        if since_ts and e.get("ts", "") < since_ts:
            break   # lines are chronological; once we're past the cutoff, stop
        entries.append(e)
        if len(entries) >= n:
            break
    return entries


# ─────────────────────────────────────────────────────────────────────────────
# SSE (Server-Sent Events) support
# ─────────────────────────────────────────────────────────────────────────────

def subscribe_sse():
    """
    Register a new SSE subscriber.
    Returns a deque that will receive new log entries as SSE-formatted strings.
    Pre-populated with the last _SSE_KEEP_LAST entries for catch-up.
    """
    q = collections.deque(maxlen=_SSE_QUEUE_MAX)
    with _sse_lock:
        # Send recent history so the client gets context immediately
        for entry in _recent_ring:
            q.append(_format_sse(entry))
        _subscribers.append(q)
    return q


def unsubscribe_sse(q: collections.deque) -> None:
    """Remove a subscriber deque."""
    with _sse_lock:
        try:
            _subscribers.remove(q)
        except ValueError:
            pass


def _push_sse(entry: dict) -> None:
    """Push a log entry to the ring buffer and all live SSE subscribers."""
    formatted = _format_sse(entry)
    with _sse_lock:
        _recent_ring.append(entry)
        dead = []
        for q in _subscribers:
            try:
                q.append(formatted)
            except Exception:
                dead.append(q)
        for q in dead:
            _subscribers.remove(q)


def _format_sse(entry: dict) -> str:
    """Format a log entry as an SSE data frame."""
    data = json.dumps(entry, separators=(",", ":"))
    tag  = entry.get("tag", "log")
    return f"event: {tag}\ndata: {data}\n\n"


# ─────────────────────────────────────────────────────────────────────────────
# Request ID helper
# ─────────────────────────────────────────────────────────────────────────────

def new_request_id() -> str:
    """Generate a short unique request ID."""
    return uuid.uuid4().hex[:12]
