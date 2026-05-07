"""
observability/telemetry.py — Worker + queue + plugin telemetry.

Aggregates telemetry from all subsystems into a single snapshot.
"""
from __future__ import annotations

import time
from typing import Any


class TelemetryCollector:
    """Collects telemetry from injected subsystems."""

    def __init__(self):
        self._start = time.time()
        self._plugin_calls: dict[str, dict] = {}   # plugin_id → {calls, errors, ms_total}

    def record_plugin_call(self, plugin_id: str, hook: str,
                           ms: float, error: bool = False) -> None:
        key = f"{plugin_id}:{hook}"
        if key not in self._plugin_calls:
            self._plugin_calls[key] = {"calls": 0, "errors": 0, "ms_total": 0.0}
        self._plugin_calls[key]["calls"]    += 1
        self._plugin_calls[key]["ms_total"] += ms
        if error:
            self._plugin_calls[key]["errors"] += 1

    def snapshot(self, queue_stats: dict | None = None,
                 worker_status: dict | None = None,
                 metrics_snap: dict | None = None) -> dict:
        plugin_telem = {}
        for key, v in self._plugin_calls.items():
            plugin_telem[key] = {
                **v,
                "avg_ms": round(v["ms_total"] / v["calls"], 2) if v["calls"] else 0,
            }
        return {
            "uptime_s":    round(time.time() - self._start),
            "queue":       queue_stats or {},
            "workers":     worker_status or {},
            "plugins":     plugin_telem,
            "metrics":     metrics_snap or {},
        }


telemetry = TelemetryCollector()
