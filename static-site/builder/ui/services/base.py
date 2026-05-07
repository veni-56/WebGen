"""
services/base.py — Base service class and shared contracts.

Every service inherits BaseService which provides:
  - access to the event bus
  - access to the DB connection
  - structured logging
  - error boundary
"""
from __future__ import annotations

import traceback
from typing import Any


class ServiceError(Exception):
    def __init__(self, message: str, code: str = "SERVICE_ERROR"):
        super().__init__(message)
        self.code = code


class BaseService:
    """Base class for all domain services."""

    service_name: str = "base"

    def __init__(self, conn=None):
        self._conn = conn

    def _bus(self):
        from core.event_bus import bus
        return bus

    def _emit(self, event_type: str, payload: dict,
              correlation_id: str = "") -> None:
        try:
            self._bus().publish(event_type, payload,
                                source=self.service_name,
                                correlation_id=correlation_id)
        except Exception:
            pass

    def _log(self, tag: str, data: dict, level: str = "INFO") -> None:
        try:
            import sys
            sys.path.insert(0, __file__.rsplit("/", 3)[0])
            from logger_server import slog
            slog(tag, {**data, "service": self.service_name}, level)
        except Exception:
            pass

    def _safe(self, fn, *args, fallback=None, **kwargs):
        """Call fn safely, returning fallback on any exception."""
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            self._log("SERVICE_ERROR", {
                "fn": getattr(fn, "__name__", str(fn)),
                "error": str(e),
                "tb": traceback.format_exc()[-300:],
            }, level="ERROR")
            return fallback
