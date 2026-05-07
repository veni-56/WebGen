"""analytics/exports.py — Analytics data export."""
from __future__ import annotations
import csv
import io
import json
import sqlite3


class AnalyticsExporter:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def to_csv(self, event_type: str | None = None,
               org_id: str | None = None, limit: int = 10000) -> str:
        sql, params = "SELECT event_type,org_id,user_id,project_id,ts FROM analytics_events WHERE 1=1", []
        if event_type: sql += " AND event_type=?"; params.append(event_type)
        if org_id:     sql += " AND org_id=?";     params.append(org_id)
        sql += " ORDER BY ts DESC LIMIT ?"
        params.append(limit)
        rows = self._conn.execute(sql, params).fetchall()
        buf  = io.StringIO()
        w    = csv.writer(buf)
        w.writerow(["event_type", "org_id", "user_id", "project_id", "ts"])
        for r in rows:
            w.writerow([r["event_type"], r["org_id"], r["user_id"], r["project_id"], r["ts"]])
        return buf.getvalue()

    def to_json(self, event_type: str | None = None,
                org_id: str | None = None, limit: int = 1000) -> str:
        sql, params = "SELECT * FROM analytics_events WHERE 1=1", []
        if event_type: sql += " AND event_type=?"; params.append(event_type)
        if org_id:     sql += " AND org_id=?";     params.append(org_id)
        sql += " ORDER BY ts DESC LIMIT ?"
        params.append(limit)
        rows = self._conn.execute(sql, params).fetchall()
        return json.dumps([dict(r) for r in rows], indent=2)

    def summary(self, org_id: str) -> dict:
        row = self._conn.execute("""
            SELECT
                COUNT(*) as total_events,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT project_id) as unique_projects,
                MIN(ts) as first_event,
                MAX(ts) as last_event
            FROM analytics_events WHERE org_id=?
        """, (org_id,)).fetchone()
        return dict(row) if row else {}
