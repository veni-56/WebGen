"""
observability/tracing.py — Distributed request tracing.

Each request gets a trace_id (UUID). Spans are nested operations within
a trace. No external service needed — traces are stored in-memory and
optionally flushed to the log file.

Usage:
    from observability.tracing import tracer

    with tracer.span("build_page", trace_id=g.trace_id) as span:
        span.set_tag("page", "home")
        do_work()
"""
from __future__ import annotations

import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Span:
    span_id:    str
    trace_id:   str
    name:       str
    parent_id:  str | None = None
    start_ms:   float      = field(default_factory=lambda: time.time() * 1000)
    end_ms:     float | None = None
    tags:       dict       = field(default_factory=dict)
    error:      str | None = None

    def set_tag(self, key: str, value: Any) -> None:
        self.tags[key] = value

    def finish(self, error: str | None = None) -> None:
        self.end_ms = time.time() * 1000
        if error:
            self.error = error

    @property
    def duration_ms(self) -> float:
        if self.end_ms is None:
            return 0.0
        return round(self.end_ms - self.start_ms, 2)

    def to_dict(self) -> dict:
        return {
            "span_id":     self.span_id,
            "trace_id":    self.trace_id,
            "name":        self.name,
            "parent_id":   self.parent_id,
            "duration_ms": self.duration_ms,
            "tags":        self.tags,
            "error":       self.error,
        }


class Tracer:
    MAX_TRACES = 500

    def __init__(self):
        self._lock   = threading.Lock()
        self._traces: dict[str, list[Span]] = {}   # trace_id → spans
        self._local  = threading.local()

    def new_trace_id(self) -> str:
        return uuid.uuid4().hex[:16]

    @contextmanager
    def span(self, name: str, trace_id: str = "", parent_id: str | None = None):
        tid  = trace_id or self.new_trace_id()
        span = Span(span_id=uuid.uuid4().hex[:8], trace_id=tid,
                    name=name, parent_id=parent_id)
        try:
            yield span
        except Exception as e:
            span.finish(error=str(e))
            raise
        finally:
            span.finish()
            self._record(span)

    def _record(self, span: Span) -> None:
        with self._lock:
            if len(self._traces) >= self.MAX_TRACES:
                oldest = next(iter(self._traces))
                del self._traces[oldest]
            self._traces.setdefault(span.trace_id, []).append(span)

    def get_trace(self, trace_id: str) -> list[dict]:
        with self._lock:
            return [s.to_dict() for s in self._traces.get(trace_id, [])]

    def get_recent(self, limit: int = 20) -> list[dict]:
        with self._lock:
            result = []
            for tid, spans in list(self._traces.items())[-limit:]:
                result.append({
                    "trace_id":    tid,
                    "spans":       len(spans),
                    "total_ms":    sum(s.duration_ms for s in spans),
                    "has_error":   any(s.error for s in spans),
                })
            return result


tracer = Tracer()
