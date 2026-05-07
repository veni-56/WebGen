"""analytics/aggregations.py — Analytics aggregation queries."""
from __future__ import annotations
import sqlite3
from datetime import datetime, timezone, timedelta


class BuildAggregator:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def by_org(self, org_id: str, days: int = 30) -> dict:
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        rows  = self._conn.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN json_extract(payload,'$.ok')=1 THEN 1 ELSE 0 END) as success,
                AVG(CAST(json_extract(payload,'$.duration_ms') AS REAL)) as avg_ms
            FROM analytics_events
            WHERE event_type='build.completed' AND org_id=? AND ts>=?
        """, (org_id, since)).fetchone()
        return dict(rows) if rows else {}

    def daily_counts(self, org_id: str, days: int = 7) -> list[dict]:
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        rows  = self._conn.execute("""
            SELECT substr(ts,1,10) as date, COUNT(*) as count
            FROM analytics_events
            WHERE event_type LIKE 'build.%' AND org_id=? AND ts>=?
            GROUP BY date ORDER BY date
        """, (org_id, since)).fetchall()
        return [dict(r) for r in rows]


class PluginAggregator:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def by_org(self, org_id: str) -> list[dict]:
        rows = self._conn.execute("""
            SELECT json_extract(payload,'$.slug') as slug, COUNT(*) as installs
            FROM analytics_events
            WHERE event_type='plugin.installed' AND org_id=?
            GROUP BY slug ORDER BY installs DESC
        """, (org_id,)).fetchall()
        return [dict(r) for r in rows]


class UserActivityAggregator:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def active_users(self, org_id: str, days: int = 30) -> int:
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        row   = self._conn.execute("""
            SELECT COUNT(DISTINCT user_id) as count
            FROM analytics_events WHERE org_id=? AND ts>=? AND user_id!=''
        """, (org_id, since)).fetchone()
        return row["count"] if row else 0
