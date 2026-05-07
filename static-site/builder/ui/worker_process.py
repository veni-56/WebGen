#!/usr/bin/env python3
"""
worker_process.py — Standalone worker entry point for the Docker worker container.

Runs the WorkerPool in the foreground, handles SIGTERM for graceful shutdown,
and registers all build handlers so jobs can be processed independently
of the web container.

Usage:
    python worker_process.py
    # or via Docker CMD
"""
import os, signal, sys, time
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
UI_DIR      = Path(__file__).parent
BUILDER_DIR = UI_DIR.parent
sys.path.insert(0, str(UI_DIR))
sys.path.insert(0, str(BUILDER_DIR))

# ── Config from environment ───────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(UI_DIR / ".env")
except ImportError:
    pass

DB_PATH      = Path(os.environ.get("DB_PATH",      str(UI_DIR / "projects.db")))
UPLOADS_DIR  = Path(os.environ.get("UPLOADS_DIR",  str(UI_DIR / "uploads")))
PUBLISH_DIR  = Path(os.environ.get("PUBLISH_DIR",  str(UI_DIR / "published")))
LOG_DIR      = Path(os.environ.get("LOG_DIR",      str(UI_DIR / "logs")))
WORKER_COUNT = int(os.environ.get("WORKER_COUNT",  "2"))

# Ensure directories exist
for d in (DB_PATH.parent, UPLOADS_DIR, PUBLISH_DIR, LOG_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── Logging ───────────────────────────────────────────────────────────────────
from logger_server import slog, capture_exception

# ── Import build dependencies ─────────────────────────────────────────────────
try:
    from build import build
except ImportError as e:
    slog("WORKER_INIT", {"error": f"build module not found: {e}"}, level="ERROR")
    sys.exit(1)

# ── Import worker ─────────────────────────────────────────────────────────────
from worker import JobQueue, WorkerPool, pool

# ── Configure queue ───────────────────────────────────────────────────────────
JobQueue.configure(DB_PATH)
pool.configure_logger(slog)

# ── Register build handlers ───────────────────────────────────────────────────

def _build_to_dir(cfg, out_dir, visual=False):
    """Inline build helper (mirrors server.py's _build_to_dir)."""
    import shutil
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    build(cfg, out_dir, mode="static", minify=False)
    css = (out_dir / "style.css").read_text(encoding="utf-8") if (out_dir / "style.css").exists() else ""
    js  = (out_dir / "script.js").read_text(encoding="utf-8") if (out_dir / "script.js").exists() else ""
    for f in out_dir.glob("*.html"):
        html = f.read_text(encoding="utf-8")
        html = html.replace('<link rel="stylesheet" href="style.css"/>', f"<style>{css}</style>")
        html = html.replace('<script src="script.js"></script>', f"<script>{js}</script>")
        f.write_text(html, encoding="utf-8")


def _publish_handler(payload: dict) -> dict:
    """Handle a publish job: build → optimize → copy to latest → update DB."""
    import json, shutil, sqlite3, hashlib
    from datetime import datetime, timezone

    cfg = payload.get("cfg") or {}
    pid = payload.get("pid", "")
    if not pid:
        raise ValueError("publish job missing 'pid'")

    t0  = time.time()
    ver = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    ver_dir = PUBLISH_DIR / pid / "versions" / ver

    slog("BUILD", {"kind": "publish", "pid": pid, "ver": ver, "step": "start"})

    # Build
    _build_to_dir(cfg, ver_dir, visual=False)

    # Optimize if available
    opt_stats = {}
    try:
        from optimize import optimize_dir
        opt_stats = optimize_dir(ver_dir)
        slog("BUILD", {"kind": "publish", "pid": pid, "step": "optimized", "stats": opt_stats})
    except Exception as e:
        slog("BUILD", {"kind": "publish", "pid": pid, "step": "optimize_skip", "reason": str(e)}, level="WARNING")

    # Copy to latest
    latest = PUBLISH_DIR / pid / "latest"
    if latest.exists():
        shutil.rmtree(latest)
    shutil.copytree(ver_dir, latest)

    # Update DB
    url     = f"/site/{pid}"
    ver_url = f"/published/{pid}/v/{ver}/index.html"
    build_ms = round((time.time() - t0) * 1000)

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        "UPDATE projects SET published=1, publish_url=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (url, pid)
    )
    conn.execute(
        "INSERT INTO publish_versions (project_id, version, url) VALUES (?,?,?)",
        (pid, ver, ver_url)
    )
    conn.commit()
    conn.close()

    slog("BUILD", {"kind": "publish", "pid": pid, "ver": ver, "ms": build_ms, "ok": True})
    return {"url": url, "version": ver, "version_url": ver_url, "build_ms": build_ms}


def _preview_handler(payload: dict) -> dict:
    """Handle a preview job: build to temp dir, return page URLs."""
    import tempfile
    cfg    = payload.get("cfg") or {}
    page   = payload.get("page", "home")
    pid    = payload.get("pid", "default")
    visual = payload.get("visual", True)

    out = Path(tempfile.gettempdir()) / f"wbs_{pid}"
    _build_to_dir(cfg, out, visual=visual)
    pages = cfg.get("pages", {})
    urls  = {k: f"/preview/{pid}/{v.get('file','index.html')}" for k, v in pages.items()}
    return {"pages": urls, "base": f"/preview/{pid}/"}


def _export_handler(payload: dict) -> dict:
    """Handle an export job: build to temp dir, zip it."""
    import re, tempfile, zipfile
    cfg  = payload.get("cfg") or {}
    mode = payload.get("mode", "static")
    out  = Path(tempfile.gettempdir()) / f"wbs_export_{mode}"
    build(cfg, out, mode=mode, minify=False)
    name = re.sub(r"[^\w-]", "_", cfg.get("site_name", "website").lower())
    zp   = Path(tempfile.gettempdir()) / f"{name}.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in out.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(out))
    return {"zip_path": str(zp), "name": name}


JobQueue.register_handler("publish", _publish_handler)
JobQueue.register_handler("preview", _preview_handler)
JobQueue.register_handler("export",  _export_handler)

# ── Recover stuck jobs from previous run ─────────────────────────────────────
recovered = JobQueue._recover_stuck()
if recovered:
    slog("WORKER_INIT", {"recovered_jobs": recovered}, level="WARNING")

# ── Graceful shutdown ─────────────────────────────────────────────────────────
_shutdown = False

def _handle_signal(signum, frame):
    global _shutdown
    slog("WORKER_SHUTDOWN", {"signal": signum})
    print(f"\n[WORKER] Signal {signum} received — finishing current jobs…", flush=True)
    _shutdown = True
    pool.shutdown(wait=True)
    sys.exit(0)

signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT,  _handle_signal)

# ── Start workers ─────────────────────────────────────────────────────────────
slog("WORKER_INIT", {"workers": WORKER_COUNT, "db": str(DB_PATH)})
print(f"[WORKER] Starting {WORKER_COUNT} worker(s) — DB: {DB_PATH}", flush=True)

pool.start(n_workers=WORKER_COUNT)

# Keep main thread alive (workers are daemon threads)
try:
    while not _shutdown:
        time.sleep(5)
        stats = JobQueue.queue_stats()
        slog("WORKER_HEARTBEAT", stats)
except KeyboardInterrupt:
    _handle_signal(signal.SIGINT, None)
