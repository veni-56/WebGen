"""notifications/inapp.py — In-app notification store."""
from __future__ import annotations
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path


def init_inapp_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS inapp_notifications (
            id         TEXT PRIMARY KEY,
            user_id    TEXT NOT NULL,
            type       TEXT NOT NULL,
            body       TEXT NOT NULL,
            read       INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_inapp_user ON inapp_notifications(user_id, read, created_at DESC)")
    conn.commit()


class InAppStore:
    def __init__(self, db_path: str | None = None):
        import os
        self._db_path = db_path or os.environ.get("DB_PATH", "./projects.db")
        try:
            conn = sqlite3.connect(self._db_path)
            init_inapp_table(conn)
            conn.close()
        except Exception:
            pass

    def push(self, user_id: str, notif_type: str, body: str) -> str:
        nid  = uuid.uuid4().hex[:12]
        now  = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(self._db_path)
        conn.execute(
            "INSERT INTO inapp_notifications (id,user_id,type,body,created_at) VALUES (?,?,?,?,?)",
            (nid, user_id, notif_type, body, now)
        )
        conn.commit(); conn.close()
        return nid

    def list_for_user(self, user_id: str, unread_only: bool = False,
                      limit: int = 50) -> list[dict]:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        sql = "SELECT * FROM inapp_notifications WHERE user_id=?"
        params = [user_id]
        if unread_only:
            sql += " AND read=0"
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def mark_read(self, user_id: str, notif_id: str) -> bool:
        conn = sqlite3.connect(self._db_path)
        n = conn.execute(
            "UPDATE inapp_notifications SET read=1 WHERE id=? AND user_id=?",
            (notif_id, user_id)
        ).rowcount
        conn.commit(); conn.close()
        return n > 0

    def unread_count(self, user_id: str) -> int:
        conn = sqlite3.connect(self._db_path)
        row  = conn.execute(
            "SELECT COUNT(*) FROM inapp_notifications WHERE user_id=? AND read=0",
            (user_id,)
        ).fetchone()
        conn.close()
        return row[0] if row else 0


inapp_store = InAppStore()
