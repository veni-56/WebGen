"""
collab/snapshots.py — Snapshot compaction for collaboration state.

Snapshots reduce replay cost: instead of replaying all ops from the
beginning, replay from the nearest snapshot + ops since that snapshot.

Compaction: when op count exceeds threshold, create a new snapshot
and discard ops before it.
"""
from __future__ import annotations

import copy
import json
import sqlite3
import threading
import time
from datetime import datetime, timezone


SNAPSHOT_INTERVAL = 50   # create snapshot every N ops
MAX_SNAPSHOTS     = 20   # keep last N snapshots per doc


class SnapshotStore:
    """Persists snapshots to SQLite."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._lock    = threading.Lock()
        self._init()

    def _init(self) -> None:
        conn = sqlite3.connect(self._db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS collab_snapshots (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id     TEXT NOT NULL,
                seq        INTEGER NOT NULL,
                state      TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(doc_id, seq)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_snap_doc ON collab_snapshots(doc_id, seq DESC)")
        conn.commit(); conn.close()

    def save(self, doc_id: str, seq: int, state: dict) -> None:
        now  = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(self._db_path)
        conn.execute(
            "INSERT OR REPLACE INTO collab_snapshots (doc_id, seq, state, created_at) VALUES (?,?,?,?)",
            (doc_id, seq, json.dumps(state), now)
        )
        # Prune old snapshots
        conn.execute("""
            DELETE FROM collab_snapshots
            WHERE doc_id=? AND id NOT IN (
                SELECT id FROM collab_snapshots WHERE doc_id=?
                ORDER BY seq DESC LIMIT ?
            )
        """, (doc_id, doc_id, MAX_SNAPSHOTS))
        conn.commit(); conn.close()

    def get_latest(self, doc_id: str) -> dict | None:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        row  = conn.execute(
            "SELECT * FROM collab_snapshots WHERE doc_id=? ORDER BY seq DESC LIMIT 1",
            (doc_id,)
        ).fetchone()
        conn.close()
        if not row:
            return None
        return {"seq": row["seq"], "state": json.loads(row["state"]),
                "created_at": row["created_at"]}

    def get_at_or_before(self, doc_id: str, seq: int) -> dict | None:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        row  = conn.execute(
            "SELECT * FROM collab_snapshots WHERE doc_id=? AND seq<=? ORDER BY seq DESC LIMIT 1",
            (doc_id, seq)
        ).fetchone()
        conn.close()
        if not row:
            return None
        return {"seq": row["seq"], "state": json.loads(row["state"])}

    def list_for_doc(self, doc_id: str) -> list[dict]:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT seq, created_at FROM collab_snapshots WHERE doc_id=? ORDER BY seq DESC",
            (doc_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class SnapshotManager:
    """
    Manages snapshot creation and compaction for a document.
    Integrates with the OperationLog.
    """

    def __init__(self, store: SnapshotStore):
        self._store = store

    def maybe_compact(self, doc_id: str, op_log, current_state: dict) -> bool:
        """
        Create a snapshot if the op count since the last snapshot
        exceeds SNAPSHOT_INTERVAL. Returns True if snapshot was created.
        """
        latest = self._store.get_latest(doc_id)
        last_seq = latest["seq"] if latest else 0
        ops_since = len(op_log.since(last_seq))
        if ops_since >= SNAPSHOT_INTERVAL:
            self._store.save(doc_id, op_log._seq, copy.deepcopy(current_state))
            op_log.clear_before(op_log._seq)
            return True
        return False

    def restore(self, doc_id: str, target_seq: int | None = None) -> dict | None:
        """
        Return the best snapshot for restoring to target_seq.
        If target_seq is None, returns the latest snapshot.
        """
        if target_seq is None:
            return self._store.get_latest(doc_id)
        return self._store.get_at_or_before(doc_id, target_seq)
