"""
analytics/collector.py — Analytics event collector.

Collects raw analytics events from all subsystems.
Stores in SQLite for aggregation.
Subscribes to the event bus to capture events automatically.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path


def init_analytics_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS analytics_events (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            org_id     TEXT NOT NULL DEFAULT '',
            user_id    TEXT NOT NULL DEFAULT '',
            project_id TEXT NOT NULL DEFAULT '',
            payload    TEXT NOT NULL DEFAULT '{}',
            ts         TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_ae_type ON analytics_events(event_type, ts);
        CREATE INDEX IF NOT EXISTS idx_ae_org  ON analytics_events(org_id, ts);
        CREATE INDEX IF NOT EXISTS idx_ae_proj ON analytics_events(project_id, ts);
    """)
    conn.commit()


class AnalyticsCollector:
    MAX_BUFFER = 200

    def __init__(self, db_path: str | None = None):
        import os
        self._db_path = db_path or os.environ.get("DB_PATH", "./projects.db")
        self._buffer: list[dict] = []
        self._lock   = threading.Lock()
        self._flush_thread: threading.Thread | None = None
        self._stop   = threading.Event()
        self._init_db()

    def _init_db(self) -> None:
        try:
            conn = sqlite3.connect(self._db_path)
            init_analytics_tables(conn)
            conn.close()
        except Exception:
            pass

    def start(self) -> None:
        """Start background flush thread and subscribe to event bus."""
        self._stop.clear()
        self._flush_thread = threading.Thread(
            target=self._flush_loop, daemon=True, name="analytics-flush"
        )
        self._flush_thread.start()
        # Subscribe to all events
        try:
            from core.event_bus import bus
            bus.subscribe("*", self._on_event, group="analytics")
        except Exception:
            pass

    def stop(self) -> None:
        self._stop.set()
        self._flush_now()

    def record(self, event_type: str, payload: dict) -> None:
        entry = {
            "event_type": event_type,
            "org_id":     payload.get("org_id", ""),
            "user_id":    payload.get("user_id", ""),
            "project_id": payload.get("project_id", ""),
            "payload":    json.dumps(payload),
            "ts":         datetime.now(timezone.utc).isoformat(),
        }
        with self._lock:
            self._buffer.append(entry)
            if len(self._buffer) >= self.MAX_BUFFER:
                self._flush_now()

    def _on_event(self, event: dict) -> None:
        self.record(event.get("type", "unknown"), event.get("payload", {}))

    def _flush_loop(self) -> None:
        while not self._stop.is_set():
            time.sleep(10)
            self._flush_now()

    def _flush_now(self) -> None:
        with self._lock:
            if not self._buffer:
                return
            batch = list(self._buffer)
            self._buffer.clear()
        try:
            conn = sqlite3.connect(self._db_path)
            conn.executemany("""
                INSERT INTO analytics_events
                    (event_type, org_id, user_id, project_id, payload, ts)
                VALUES (:event_type, :org_id, :user_id, :project_id, :payload, :ts)
            """, batch)
            conn.commit(); conn.close()
        except Exception:
            pass

    def query(self, event_type: str | None = None, org_id: str | None = None,
              since: str | None = None, limit: int = 100) -> list[dict]:
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            sql, params = "SELECT * FROM analytics_events WHERE 1=1", []
            if event_type: sql += " AND event_type=?"; params.append(event_type)
            if org_id:     sql += " AND org_id=?";     params.append(org_id)
            if since:      sql += " AND ts>=?";        params.append(since)
            sql += " ORDER BY ts DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(sql, params).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception:
            return []


collector = AnalyticsCollector()
