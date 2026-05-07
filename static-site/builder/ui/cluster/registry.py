"""
cluster/registry.py — Worker cluster registry.

Tracks all worker processes: their capabilities, status, and load.
Workers self-register on startup and send heartbeats.
The coordinator uses this registry for job routing.
"""
from __future__ import annotations

import sqlite3
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


WORKER_TTL = 60   # seconds before a worker is considered dead


def init_cluster_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS cluster_workers (
            id           TEXT PRIMARY KEY,
            hostname     TEXT NOT NULL DEFAULT '',
            pid          INTEGER NOT NULL DEFAULT 0,
            capabilities TEXT NOT NULL DEFAULT '[]',
            status       TEXT NOT NULL DEFAULT 'idle'
                            CHECK(status IN ('idle','busy','draining','offline')),
            load         REAL NOT NULL DEFAULT 0.0,
            jobs_done    INTEGER NOT NULL DEFAULT 0,
            registered_at TEXT NOT NULL,
            last_beat    TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_cluster_status
            ON cluster_workers(status, last_beat);
    """)
    conn.commit()


class WorkerRegistry:
    def __init__(self, db_path: str | Path):
        self._db_path = str(db_path)
        self._lock    = threading.Lock()
        conn = sqlite3.connect(self._db_path)
        init_cluster_tables(conn)
        conn.close()

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self._db_path)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL")
        return c

    def register(self, worker_id: str, hostname: str, pid: int,
                 capabilities: list[str]) -> None:
        import json
        now  = datetime.now(timezone.utc).isoformat()
        conn = self._conn()
        conn.execute("""
            INSERT OR REPLACE INTO cluster_workers
                (id, hostname, pid, capabilities, status, registered_at, last_beat)
            VALUES (?,?,?,?,?,?,?)
        """, (worker_id, hostname, pid, json.dumps(capabilities), "idle", now, now))
        conn.commit(); conn.close()

    def heartbeat(self, worker_id: str, status: str = "idle",
                  load: float = 0.0, jobs_done: int = 0) -> None:
        now  = datetime.now(timezone.utc).isoformat()
        conn = self._conn()
        conn.execute("""
            UPDATE cluster_workers
            SET status=?, load=?, jobs_done=?, last_beat=?
            WHERE id=?
        """, (status, load, jobs_done, now, worker_id))
        conn.commit(); conn.close()

    def deregister(self, worker_id: str) -> None:
        conn = self._conn()
        conn.execute("UPDATE cluster_workers SET status='offline' WHERE id=?", (worker_id,))
        conn.commit(); conn.close()

    def list_alive(self) -> list[dict]:
        import json
        cutoff = datetime.now(timezone.utc).isoformat()
        # Subtract TTL manually
        from datetime import timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(seconds=WORKER_TTL)).isoformat()
        conn   = self._conn()
        rows   = conn.execute(
            "SELECT * FROM cluster_workers WHERE last_beat > ? AND status != 'offline'",
            (cutoff,)
        ).fetchall()
        conn.close()
        result = []
        for r in rows:
            d = dict(r)
            d["capabilities"] = json.loads(d["capabilities"])
            result.append(d)
        return result

    def list_capable(self, job_type: str) -> list[dict]:
        """Return workers that can handle a given job type."""
        return [w for w in self.list_alive()
                if job_type in w["capabilities"] or "*" in w["capabilities"]]

    def mark_draining(self, worker_id: str) -> None:
        conn = self._conn()
        conn.execute("UPDATE cluster_workers SET status='draining' WHERE id=?", (worker_id,))
        conn.commit(); conn.close()

    def cleanup_dead(self) -> int:
        from datetime import timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(seconds=WORKER_TTL * 2)).isoformat()
        conn   = self._conn()
        n = conn.execute(
            "DELETE FROM cluster_workers WHERE last_beat < ?", (cutoff,)
        ).rowcount
        conn.commit(); conn.close()
        return n

    def stats(self) -> dict:
        conn  = self._conn()
        rows  = conn.execute(
            "SELECT status, COUNT(*) as n FROM cluster_workers GROUP BY status"
        ).fetchall()
        conn.close()
        return {r["status"]: r["n"] for r in rows}
