"""
worker.py — Persistent SQLite-backed job queue and worker system.

Architecture:
  - Jobs are rows in the `jobs` table (SQLite WAL mode).
  - Workers claim jobs with a SELECT … FOR UPDATE equivalent using
    a SQLite UPDATE … WHERE status='queued' + RETURNING, which is
    atomic under WAL.  Multiple workers can run safely.
  - Retry with exponential backoff (max 3 attempts).
  - Dead-job recovery: jobs stuck in 'running' for > STUCK_TIMEOUT
    are reset to 'queued' on startup and periodically.
  - Priority: publish (10) > preview (5) > export (1).
  - Graceful shutdown: workers finish the current job before exiting.

Public API (used by server.py):
  JobQueue.enqueue(job_type, payload, priority)  -> job_id
  JobQueue.get_job(job_id)                       -> dict | None
  JobQueue.list_jobs(status, limit)              -> list[dict]
  JobQueue.queue_stats()                         -> dict
  WorkerPool.start(n_workers)
  WorkerPool.shutdown(wait)

Job handlers are registered with:
  JobQueue.register_handler(job_type, fn)
  fn(payload: dict) -> dict   (return value becomes result_json)
"""
import json, math, sqlite3, sys, threading, time, traceback, uuid
from datetime import datetime, timezone
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
MAX_RETRIES    = 3
BACKOFF_BASE   = 2.0      # seconds; delay = BACKOFF_BASE ** attempt
STUCK_TIMEOUT  = 300      # seconds before a 'running' job is considered dead
POLL_INTERVAL  = 0.5      # seconds between queue polls when idle
RECOVERY_EVERY = 60       # seconds between dead-job recovery sweeps

# Job priorities (higher = processed first)
PRIORITY = {"publish": 10, "preview": 5, "export": 1}

# ─────────────────────────────────────────────────────────────────────────────
# DB helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_conn(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_jobs_table(db_path: str | Path) -> None:
    """Create the jobs table if it doesn't exist. Safe to call multiple times."""
    conn = _get_conn(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            id           TEXT PRIMARY KEY,
            type         TEXT NOT NULL,
            status       TEXT NOT NULL DEFAULT 'queued',
            priority     INTEGER NOT NULL DEFAULT 5,
            payload      TEXT NOT NULL DEFAULT '{}',
            result       TEXT,
            error        TEXT,
            retries      INTEGER NOT NULL DEFAULT 0,
            worker_id    TEXT,
            created_at   TEXT NOT NULL,
            updated_at   TEXT NOT NULL,
            run_after    TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_jobs_status_priority
            ON jobs (status, priority DESC, created_at ASC);
        CREATE INDEX IF NOT EXISTS idx_jobs_updated
            ON jobs (updated_at);
    """)
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# JobQueue
# ─────────────────────────────────────────────────────────────────────────────

class JobQueue:
    """
    SQLite-backed persistent job queue.
    Thread-safe: each operation opens its own connection.
    """

    _handlers: dict[str, callable] = {}
    _db_path: Path = None

    @classmethod
    def configure(cls, db_path: str | Path) -> None:
        cls._db_path = Path(db_path)
        init_jobs_table(cls._db_path)

    @classmethod
    def register_handler(cls, job_type: str, fn: callable) -> None:
        """Register a handler function for a job type."""
        cls._handlers[job_type] = fn

    @classmethod
    def enqueue(cls, job_type: str, payload: dict,
                priority: int | None = None) -> str:
        """
        Insert a new job into the queue.
        Returns the job ID.
        """
        if cls._db_path is None:
            raise RuntimeError("JobQueue not configured — call JobQueue.configure(db_path)")
        jid  = uuid.uuid4().hex[:16]
        pri  = priority if priority is not None else PRIORITY.get(job_type, 5)
        now  = _now()
        conn = _get_conn(cls._db_path)
        conn.execute(
            "INSERT INTO jobs (id,type,status,priority,payload,created_at,updated_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (jid, job_type, "queued", pri, json.dumps(payload), now, now)
        )
        conn.commit()
        conn.close()
        return jid

    @classmethod
    def get_job(cls, jid: str) -> dict | None:
        """Return a job dict by ID, or None if not found."""
        conn = _get_conn(cls._db_path)
        row  = conn.execute("SELECT * FROM jobs WHERE id=?", (jid,)).fetchone()
        conn.close()
        return _row_to_dict(row) if row else None

    @classmethod
    def list_jobs(cls, status: str | None = None, limit: int = 50) -> list[dict]:
        """Return recent jobs, optionally filtered by status."""
        conn = _get_conn(cls._db_path)
        if status:
            rows = conn.execute(
                "SELECT * FROM jobs WHERE status=? ORDER BY updated_at DESC LIMIT ?",
                (status, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM jobs ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        conn.close()
        return [_row_to_dict(r) for r in rows]

    @classmethod
    def queue_stats(cls) -> dict:
        """Return counts by status."""
        conn  = _get_conn(cls._db_path)
        rows  = conn.execute(
            "SELECT status, COUNT(*) as n FROM jobs GROUP BY status"
        ).fetchall()
        conn.close()
        stats = {"queued": 0, "running": 0, "done": 0, "failed": 0}
        for r in rows:
            stats[r["status"]] = r["n"]
        stats["total"] = sum(stats.values())
        return stats

    @classmethod
    def _claim_next(cls, worker_id: str) -> dict | None:
        """
        Atomically claim the highest-priority queued job.
        Returns the job dict or None if queue is empty.
        Uses a SQLite UPDATE with WHERE to avoid double-claiming.
        """
        conn = _get_conn(cls._db_path)
        now  = _now()
        try:
            # Find the best candidate
            row = conn.execute(
                "SELECT id FROM jobs "
                "WHERE status='queued' AND (run_after IS NULL OR run_after <= ?) "
                "ORDER BY priority DESC, created_at ASC LIMIT 1",
                (now,)
            ).fetchone()
            if not row:
                conn.close()
                return None
            jid = row["id"]
            # Claim it atomically
            affected = conn.execute(
                "UPDATE jobs SET status='running', worker_id=?, updated_at=? "
                "WHERE id=? AND status='queued'",
                (worker_id, now, jid)
            ).rowcount
            conn.commit()
            if affected == 0:
                # Another worker grabbed it first
                conn.close()
                return None
            job = conn.execute("SELECT * FROM jobs WHERE id=?", (jid,)).fetchone()
            conn.close()
            return _row_to_dict(job)
        except Exception:
            conn.close()
            return None

    @classmethod
    def _mark_done(cls, jid: str, result: dict) -> None:
        conn = _get_conn(cls._db_path)
        conn.execute(
            "UPDATE jobs SET status='done', result=?, error=NULL, updated_at=? WHERE id=?",
            (json.dumps(result), _now(), jid)
        )
        conn.commit()
        conn.close()

    @classmethod
    def _mark_failed(cls, jid: str, error: str, retries: int) -> None:
        """Mark job as failed or re-queue with backoff if retries remain."""
        conn = _get_conn(cls._db_path)
        if retries < MAX_RETRIES:
            delay     = BACKOFF_BASE ** retries
            run_after = _now_plus(delay)
            conn.execute(
                "UPDATE jobs SET status='queued', error=?, retries=?, "
                "worker_id=NULL, run_after=?, updated_at=? WHERE id=?",
                (error, retries, run_after, _now(), jid)
            )
        else:
            conn.execute(
                "UPDATE jobs SET status='failed', error=?, retries=?, updated_at=? WHERE id=?",
                (error, retries, _now(), jid)
            )
        conn.commit()
        conn.close()

    @classmethod
    def _recover_stuck(cls) -> int:
        """Reset jobs stuck in 'running' for > STUCK_TIMEOUT back to 'queued'."""
        cutoff = _now_minus(STUCK_TIMEOUT)
        conn   = _get_conn(cls._db_path)
        n = conn.execute(
            "UPDATE jobs SET status='queued', worker_id=NULL, updated_at=? "
            "WHERE status='running' AND updated_at < ?",
            (_now(), cutoff)
        ).rowcount
        conn.commit()
        conn.close()
        return n


# ─────────────────────────────────────────────────────────────────────────────
# Worker
# ─────────────────────────────────────────────────────────────────────────────

class Worker(threading.Thread):
    """
    A single worker thread that polls the job queue and processes jobs.
    """

    def __init__(self, worker_id: str, logger=None):
        super().__init__(name=f"worker-{worker_id}", daemon=True)
        self.worker_id  = worker_id
        self._logger    = logger
        self._stop_evt  = threading.Event()
        self._busy      = False

    @property
    def is_busy(self) -> bool:
        return self._busy

    def stop(self, wait: bool = True) -> None:
        """Signal the worker to stop after finishing the current job."""
        self._stop_evt.set()
        if wait:
            self.join(timeout=STUCK_TIMEOUT + 10)

    def run(self) -> None:
        self._log("WORKER_START", {"worker_id": self.worker_id})
        while not self._stop_evt.is_set():
            job = JobQueue._claim_next(self.worker_id)
            if job is None:
                time.sleep(POLL_INTERVAL)
                continue
            self._process(job)
        self._log("WORKER_STOP", {"worker_id": self.worker_id})

    def _process(self, job: dict) -> None:
        jid     = job["id"]
        jtype   = job["type"]
        retries = job.get("retries", 0)
        self._busy = True
        self._log("JOB_START", {"job_id": jid, "type": jtype, "attempt": retries + 1})

        try:
            payload = job.get("payload") or {}
            if isinstance(payload, str):
                payload = json.loads(payload)
            handler = JobQueue._handlers.get(jtype)
            if handler is None:
                raise ValueError(f"No handler registered for job type '{jtype}'")
            result = handler(payload)
            JobQueue._mark_done(jid, result or {})
            self._log("JOB_SUCCESS", {"job_id": jid, "type": jtype,
                                       "attempt": retries + 1})
        except Exception as exc:
            tb    = traceback.format_exc()
            error = f"{type(exc).__name__}: {exc}"
            self._log("JOB_FAIL", {
                "job_id":  jid,
                "type":    jtype,
                "attempt": retries + 1,
                "error":   error,
                "will_retry": retries + 1 < MAX_RETRIES,
            }, level="WARNING")
            JobQueue._mark_failed(jid, error, retries + 1)
        finally:
            self._busy = False

    def _log(self, tag: str, data: dict, level: str = "INFO") -> None:
        if self._logger:
            try:
                self._logger(tag, data, level)
            except Exception:
                pass
        else:
            print(f"[{tag}] {json.dumps(data)}", file=sys.stderr)


# ─────────────────────────────────────────────────────────────────────────────
# WorkerPool
# ─────────────────────────────────────────────────────────────────────────────

class WorkerPool:
    """
    Manages a pool of Worker threads + a recovery sweep thread.
    """

    def __init__(self):
        self._workers: list[Worker] = []
        self._recovery_thread: threading.Thread | None = None
        self._stop_evt = threading.Event()
        self._logger   = None

    def configure_logger(self, logger_fn) -> None:
        self._logger = logger_fn

    def start(self, n_workers: int = 2) -> None:
        """Start n_workers worker threads and the recovery sweep."""
        for i in range(n_workers):
            wid = f"{uuid.uuid4().hex[:6]}-{i}"
            w   = Worker(wid, logger=self._logger)
            w.start()
            self._workers.append(w)

        # Recovery sweep thread
        self._recovery_thread = threading.Thread(
            target=self._recovery_loop, daemon=True, name="job-recovery"
        )
        self._recovery_thread.start()

        if self._logger:
            self._logger("POOL_START", {"workers": n_workers})

    def shutdown(self, wait: bool = True) -> None:
        """Signal all workers to stop gracefully."""
        self._stop_evt.set()
        for w in self._workers:
            w.stop(wait=wait)
        if self._logger:
            self._logger("POOL_STOP", {"workers": len(self._workers)})

    def status(self) -> dict:
        return {
            "total":  len(self._workers),
            "busy":   sum(1 for w in self._workers if w.is_busy),
            "idle":   sum(1 for w in self._workers if not w.is_busy),
            "alive":  sum(1 for w in self._workers if w.is_alive()),
        }

    def _recovery_loop(self) -> None:
        """Periodically reset stuck jobs."""
        while not self._stop_evt.is_set():
            time.sleep(RECOVERY_EVERY)
            try:
                n = JobQueue._recover_stuck()
                if n > 0 and self._logger:
                    self._logger("JOB_RECOVERY", {"reset": n}, "WARNING")
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

def _now_plus(seconds: float) -> str:
    from datetime import timedelta
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat(timespec="milliseconds")

def _now_minus(seconds: float) -> str:
    from datetime import timedelta
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds)).isoformat(timespec="milliseconds")

def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    # Parse JSON fields — they may already be dicts if previously parsed
    for field in ("payload", "result"):
        v = d.get(field)
        if isinstance(v, str):
            try:
                d[field] = json.loads(v)
            except Exception:
                pass
        elif v is None:
            d[field] = {}
    return d


# ─────────────────────────────────────────────────────────────────────────────
# Singleton pool (used by server.py)
# ─────────────────────────────────────────────────────────────────────────────
pool = WorkerPool()
