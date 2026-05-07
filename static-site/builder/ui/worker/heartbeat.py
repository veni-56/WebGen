"""
worker/heartbeat.py — Worker heartbeat system.

Each worker process writes a heartbeat row to the DB every N seconds.
The scheduler uses this to detect dead workers and recover their jobs.

Table: worker_heartbeats (worker_id TEXT PK, pid INT, started_at TEXT, last_beat TEXT, jobs_done INT)
"""
from __future__ import annotations

import os
import sqlite3
import threading
import time
from datetime import datetime, timezone


HEARTBEAT_INTERVAL = 15   # seconds
WORKER_DEAD_AFTER  = 60   # seconds without heartbeat = dead


def init_heartbeat_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS worker_heartbeats (
            worker_id  TEXT PRIMARY KEY,
            pid        INTEGER NOT NULL,
            started_at TEXT NOT NULL,
            last_beat  TEXT NOT NULL,
            jobs_done  INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()


class WorkerHeartbeat:
    def __init__(self, worker_id: str, db_path: str):
        self._worker_id = worker_id
        self._db_path   = db_path
        self._jobs_done = 0
        self._stop      = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._register()
        self._thread = threading.Thread(target=self._loop, daemon=True,
                                        name=f"heartbeat-{self._worker_id}")
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._deregister()

    def increment(self) -> None:
        self._jobs_done += 1

    def _register(self) -> None:
        conn = sqlite3.connect(self._db_path)
        now  = datetime.now(timezone.utc).isoformat()
        conn.execute("""
            INSERT OR REPLACE INTO worker_heartbeats
                (worker_id, pid, started_at, last_beat, jobs_done)
            VALUES (?,?,?,?,?)
        """, (self._worker_id, os.getpid(), now, now, 0))
        conn.commit(); conn.close()

    def _beat(self) -> None:
        conn = sqlite3.connect(self._db_path)
        now  = datetime.now(timezone.utc).isoformat()
        conn.execute("""
            UPDATE worker_heartbeats
            SET last_beat=?, jobs_done=?
            WHERE worker_id=?
        """, (now, self._jobs_done, self._worker_id))
        conn.commit(); conn.close()

    def _deregister(self) -> None:
        try:
            conn = sqlite3.connect(self._db_path)
            conn.execute("DELETE FROM worker_heartbeats WHERE worker_id=?",
                         (self._worker_id,))
            conn.commit(); conn.close()
        except Exception:
            pass

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self._beat()
            except Exception:
                pass
            time.sleep(HEARTBEAT_INTERVAL)


def get_dead_workers(conn: sqlite3.Connection) -> list[str]:
    """Return worker IDs that haven't beaten in WORKER_DEAD_AFTER seconds."""
    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(seconds=WORKER_DEAD_AFTER)).isoformat()
    rows = conn.execute(
        "SELECT worker_id FROM worker_heartbeats WHERE last_beat < ?", (cutoff,)
    ).fetchall()
    return [r[0] for r in rows]


def list_workers(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM worker_heartbeats ORDER BY started_at").fetchall()
    return [dict(r) for r in rows]
