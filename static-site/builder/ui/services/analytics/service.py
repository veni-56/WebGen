"""services/analytics/service.py — Analytics domain service."""
from __future__ import annotations
from services.base import BaseService


class AnalyticsService(BaseService):
    service_name = "analytics"

    def record(self, event_type: str, payload: dict) -> None:
        """Record an analytics event (delegated to analytics pipeline)."""
        try:
            from analytics.collector import collector
            collector.record(event_type, payload)
        except Exception:
            pass

    def get_build_stats(self, org_id: str, days: int = 30) -> dict:
        try:
            from analytics.aggregations import BuildAggregator
            return BuildAggregator(self._conn).by_org(org_id, days)
        except Exception:
            return {}

    def get_plugin_usage(self, org_id: str) -> list[dict]:
        try:
            from analytics.aggregations import PluginAggregator
            return PluginAggregator(self._conn).by_org(org_id)
        except Exception:
            return []
