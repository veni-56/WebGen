"""
worker/retry.py — Retry policy and dead-letter queue.

Provides:
  RetryPolicy   — configurable backoff strategy
  DeadLetterQueue — stores permanently failed jobs for inspection
"""
from __future__ import annotations

import json
import math
import sqlite3
import time
import uuid
from datetime import datetime, timezone


# ── Retry policy ──────────────────────────────────────────────────────────────

class RetryPolicy:
    """
    Configurable retry policy with exponential backoff + jitter.

    delay(attempt) = base * (multiplier ** attempt) + jitter
    """

    def __init__(self, max_retries: int = 3, base_delay: float = 2.0,
                 multiplier: float = 2.0, max_delay: float = 300.0,
                 jitter: float = 0.5):
        self.max_retries = max_retries
        self.base_delay  = base_delay
        self.multiplier  = multiplier
        self.max_delay   = max_delay
        self.jitter      = jitter

    def should_retry(self, attempt: int) -> bool:
        return attempt < self.max_retries

    def delay(self, attempt: int) -> float:
        """Return seconds to wait before attempt N."""
        raw   = self.base_delay * (self.multiplier ** attempt)
        capped = min(raw, self.max_delay)
        import random
        jitter = random.uniform(0, self.jitter)
        return round(capped + jitter, 2)

    def next_run_at(self, attempt: int) -> str:
        """Return ISO timestamp for when the job should next run."""
        from datetime import timedelta
        delay = self.delay(attempt)
        return (datetime.now(timezone.utc) + timedelta(seconds=delay)).isoformat()


# Default policy used by the worker
DEFAULT_POLICY = RetryPolicy(max_retries=3, base_delay=2.0, multiplier=2.0)


# ── Dead-letter queue ─────────────────────────────────────────────────────────

def init_dlq_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dead_letter_queue (
            id          TEXT PRIMARY KEY,
            job_id      TEXT NOT NULL,
            job_type    TEXT NOT NULL,
            payload     TEXT NOT NULL,
            error       TEXT NOT NULL,
            retries     INTEGER NOT NULL DEFAULT 0,
            failed_at   TEXT NOT NULL,
            resolved    INTEGER NOT NULL DEFAULT 0,
            resolved_at TEXT
        )
    """)
    conn.commit()


class DeadLetterQueue:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        init_dlq_table(conn)

    def push(self, job_id: str, job_type: str, payload: dict,
             error: str, retries: int) -> str:
        dlq_id = str(uuid.uuid4())
        now    = datetime.now(timezone.utc).isoformat()
        self._conn.execute("""
            INSERT INTO dead_letter_queue
                (id, job_id, job_type, payload, error, retries, failed_at)
            VALUES (?,?,?,?,?,?,?)
        """, (dlq_id, job_id, job_type, json.dumps(payload), error, retries, now))
        self._conn.commit()
        return dlq_id

    def list_unresolved(self, limit: int = 50) -> list[dict]:
        rows = self._conn.execute("""
            SELECT * FROM dead_letter_queue
            WHERE resolved=0
            ORDER BY failed_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def resolve(self, dlq_id: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        n = self._conn.execute("""
            UPDATE dead_letter_queue
            SET resolved=1, resolved_at=?
            WHERE id=?
        """, (now, dlq_id)).rowcount
        self._conn.commit()
        return n > 0

    def requeue(self, dlq_id: str, job_queue) -> bool:
        """Re-enqueue a dead-letter job."""
        row = self._conn.execute(
            "SELECT * FROM dead_letter_queue WHERE id=?", (dlq_id,)
        ).fetchone()
        if not row:
            return False
        d = dict(row)
        payload = json.loads(d["payload"])
        job_queue.enqueue(d["job_type"], payload, priority=1)
        self.resolve(dlq_id)
        return True

    def stats(self) -> dict:
        row = self._conn.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN resolved=0 THEN 1 ELSE 0 END) as unresolved,
                SUM(CASE WHEN resolved=1 THEN 1 ELSE 0 END) as resolved
            FROM dead_letter_queue
        """).fetchone()
        return dict(row) if row else {}
