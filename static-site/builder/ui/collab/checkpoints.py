"""
collab/checkpoints.py — Collaborative checkpoint system.

Checkpoints are named restore points created by users or automatically.
Unlike snapshots (automatic, internal), checkpoints are user-visible
and can be restored on demand.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone


class CheckpointStore:
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._init()

    def _init(self) -> None:
        conn = sqlite3.connect(self._db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS collab_checkpoints (
                id         TEXT PRIMARY KEY,
                doc_id     TEXT NOT NULL,
                name       TEXT NOT NULL,
                seq        INTEGER NOT NULL,
                state      TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cp_doc ON collab_checkpoints(doc_id, created_at DESC)")
        conn.commit(); conn.close()

    def create(self, doc_id: str, name: str, seq: int,
               state: dict, created_by: str) -> str:
        cid  = uuid.uuid4().hex[:12]
        now  = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(self._db_path)
        conn.execute(
            "INSERT INTO collab_checkpoints (id,doc_id,name,seq,state,created_by,created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (cid, doc_id, name, seq, json.dumps(state), created_by, now)
        )
        conn.commit(); conn.close()
        return cid

    def get(self, checkpoint_id: str) -> dict | None:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        row  = conn.execute(
            "SELECT * FROM collab_checkpoints WHERE id=?", (checkpoint_id,)
        ).fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        d["state"] = json.loads(d["state"])
        return d

    def list_for_doc(self, doc_id: str, limit: int = 20) -> list[dict]:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id,name,seq,created_by,created_at FROM collab_checkpoints "
            "WHERE doc_id=? ORDER BY created_at DESC LIMIT ?",
            (doc_id, limit)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def delete(self, checkpoint_id: str) -> bool:
        conn = sqlite3.connect(self._db_path)
        n = conn.execute(
            "DELETE FROM collab_checkpoints WHERE id=?", (checkpoint_id,)
        ).rowcount
        conn.commit(); conn.close()
        return n > 0
