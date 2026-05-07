"""
worker/locks.py — Distributed locking via SQLite.

Provides advisory locks stored in a `distributed_locks` table.
Safe for multi-process use (SQLite WAL + busy_timeout).
Locks expire automatically after TTL seconds.

Usage:
    from worker.locks import DistributedLock
    with DistributedLock(conn, 'publish:project_abc', ttl=120):
        # only one worker runs this at a time
        do_publish()
"""
from __future__ import annotations

import sqlite3
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta


def init_locks_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS distributed_locks (
            key        TEXT PRIMARY KEY,
            owner      TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
    """)
    conn.commit()


class LockError(Exception):
    pass


class DistributedLock:
    def __init__(self, conn: sqlite3.Connection, key: str,
                 ttl: float = 60, retry: int = 3, retry_delay: float = 0.5):
        self._conn        = conn
        self._key         = key
        self._ttl         = ttl
        self._retry       = retry
        self._retry_delay = retry_delay
        self._owner       = uuid.uuid4().hex

    def acquire(self) -> bool:
        now     = datetime.now(timezone.utc)
        expires = (now + timedelta(seconds=self._ttl)).isoformat()
        now_iso = now.isoformat()

        for attempt in range(self._retry):
            try:
                # Delete expired lock first
                self._conn.execute(
                    "DELETE FROM distributed_locks WHERE key=? AND expires_at < ?",
                    (self._key, now_iso)
                )
                self._conn.execute(
                    "INSERT INTO distributed_locks (key, owner, expires_at) VALUES (?,?,?)",
                    (self._key, self._owner, expires)
                )
                self._conn.commit()
                return True
            except sqlite3.IntegrityError:
                if attempt < self._retry - 1:
                    time.sleep(self._retry_delay * (2 ** attempt))
        return False

    def release(self) -> None:
        self._conn.execute(
            "DELETE FROM distributed_locks WHERE key=? AND owner=?",
            (self._key, self._owner)
        )
        self._conn.commit()

    def __enter__(self):
        if not self.acquire():
            raise LockError(f"Could not acquire lock: {self._key}")
        return self

    def __exit__(self, *_):
        self.release()


@contextmanager
def advisory_lock(conn: sqlite3.Connection, key: str, ttl: float = 60):
    lock = DistributedLock(conn, key, ttl=ttl)
    with lock:
        yield
