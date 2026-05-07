"""analytics/funnels.py — Conversion funnel analysis."""
from __future__ import annotations
import sqlite3
from datetime import datetime, timezone, timedelta


class FunnelAnalyzer:
    """
    Tracks user progression through defined funnel steps.
    Example funnel: register → create_project → publish → deploy
    """

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def analyze(self, steps: list[str], org_id: str = "",
                days: int = 30) -> list[dict]:
        since  = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        result = []
        prev_users: set[str] | None = None

        for step in steps:
            sql    = "SELECT DISTINCT user_id FROM analytics_events WHERE event_type=? AND ts>=? AND user_id!=''"
            params = [step, since]
            if org_id:
                sql += " AND org_id=?"
                params.append(org_id)
            rows  = self._conn.execute(sql, params).fetchall()
            users = {r["user_id"] for r in rows}

            if prev_users is not None:
                users = users & prev_users   # only users who completed previous step

            result.append({
                "step":       step,
                "users":      len(users),
                "conversion": round(len(users) / len(prev_users) * 100, 1) if prev_users else 100.0,
            })
            prev_users = users

        return result

    def drop_off(self, steps: list[str], org_id: str = "",
                 days: int = 30) -> list[dict]:
        funnel = self.analyze(steps, org_id, days)
        result = []
        for i, step in enumerate(funnel):
            prev = funnel[i-1]["users"] if i > 0 else step["users"]
            result.append({
                **step,
                "drop_off": prev - step["users"],
                "drop_off_pct": round((prev - step["users"]) / prev * 100, 1) if prev else 0,
            })
        return result
