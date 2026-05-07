"""
cluster/leases.py — Job leasing for distributed workers.

A lease is an exclusive claim on a job by a worker.
Prevents double-processing in a multi-worker cluster.
Leases expire automatically (TTL) so crashed workers release jobs.
"""
from __future__ import annotations

import sqlite3
import threading
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path


LEASE_TTL = 120   # seconds


def init_lease_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS job_leases (
            job_id     TEXT PRIMARY KEY,
            worker_id  TEXT NOT NULL,
            lease_id   TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            acquired_at TEXT NOT NULL
        )
    """)
    conn.commit()


class LeaseManager:
    def __init__(self, db_path: str | Path):
        self._db_path = str(db_path)
        conn = sqlite3.connect(self._db_path)
        init_lease_table(conn)
        conn.close()

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self._db_path)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA busy_timeout=3000")
        return c

    def acquire(self, job_id: str, worker_id: str,
                ttl: int = LEASE_TTL) -> str | None:
        """
        Try to acquire a lease on job_id for worker_id.
        Returns lease_id on success, None if already leased.
        """
        now     = datetime.now(timezone.utc)
        expires = (now + timedelta(seconds=ttl)).isoformat()
        now_iso = now.isoformat()
        lid     = uuid.uuid4().hex[:12]
        conn    = self._conn()
        try:
            # Remove expired lease first
            conn.execute(
                "DELETE FROM job_leases WHERE job_id=? AND expires_at < ?",
                (job_id, now_iso)
            )
            conn.execute(
                "INSERT INTO job_leases (job_id,worker_id,lease_id,expires_at,acquired_at) "
                "VALUES (?,?,?,?,?)",
                (job_id, worker_id, lid, expires, now_iso)
            )
            conn.commit()
            return lid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def renew(self, job_id: str, lease_id: str,
              ttl: int = LEASE_TTL) -> bool:
        expires = (datetime.now(timezone.utc) + timedelta(seconds=ttl)).isoformat()
        conn    = self._conn()
        n = conn.execute(
            "UPDATE job_leases SET expires_at=? WHERE job_id=? AND lease_id=?",
            (expires, job_id, lease_id)
        ).rowcount
        conn.commit(); conn.close()
        return n > 0

    def release(self, job_id: str, lease_id: str) -> bool:
        conn = self._conn()
        n = conn.execute(
            "DELETE FROM job_leases WHERE job_id=? AND lease_id=?",
            (job_id, lease_id)
        ).rowcount
        conn.commit(); conn.close()
        return n > 0

    def is_leased(self, job_id: str) -> bool:
        now  = datetime.now(timezone.utc).isoformat()
        conn = self._conn()
        row  = conn.execute(
            "SELECT 1 FROM job_leases WHERE job_id=? AND expires_at > ?",
            (job_id, now)
        ).fetchone()
        conn.close()
        return row is not None

    def cleanup_expired(self) -> int:
        now  = datetime.now(timezone.utc).isoformat()
        conn = self._conn()
        n = conn.execute(
            "DELETE FROM job_leases WHERE expires_at < ?", (now,)
        ).rowcount
        conn.commit(); conn.close()
        return n
