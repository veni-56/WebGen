"""
observability/spans.py — Distributed span trees for cross-service tracing.

Extends the existing tracing.py with:
- Parent-child span relationships
- Cross-service trace propagation headers
- Span context injection/extraction
"""
from __future__ import annotations

import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SpanContext:
    trace_id:   str
    span_id:    str
    parent_id:  str | None = None
    baggage:    dict = field(default_factory=dict)

    def to_headers(self) -> dict[str, str]:
        return {
            "X-Trace-ID":  self.trace_id,
            "X-Span-ID":   self.span_id,
            "X-Parent-ID": self.parent_id or "",
        }

    @classmethod
    def from_headers(cls, headers: dict) -> "SpanContext":
        return cls(
            trace_id  = headers.get("X-Trace-ID")  or uuid.uuid4().hex[:16],
            span_id   = headers.get("X-Span-ID")   or uuid.uuid4().hex[:8],
            parent_id = headers.get("X-Parent-ID") or None,
        )

    def child(self) -> "SpanContext":
        return SpanContext(
            trace_id  = self.trace_id,
            span_id   = uuid.uuid4().hex[:8],
            parent_id = self.span_id,
            baggage   = dict(self.baggage),
        )


@dataclass
class DistributedSpan:
    ctx:        SpanContext
    name:       str
    service:    str = "wbs"
    start_ms:   float = field(default_factory=lambda: time.time() * 1000)
    end_ms:     float = 0.0
    tags:       dict  = field(default_factory=dict)
    logs:       list  = field(default_factory=list)
    error:      str   = ""

    def set_tag(self, k: str, v: Any) -> None:
        self.tags[k] = v

    def log(self, msg: str) -> None:
        self.logs.append({"ts": time.time() * 1000, "msg": msg})

    def finish(self, error: str = "") -> None:
        self.end_ms = time.time() * 1000
        if error:
            self.error = error

    @property
    def duration_ms(self) -> float:
        return round(self.end_ms - self.start_ms, 2) if self.end_ms else 0.0

    def to_dict(self) -> dict:
        return {
            "trace_id":    self.ctx.trace_id,
            "span_id":     self.ctx.span_id,
            "parent_id":   self.ctx.parent_id,
            "name":        self.name,
            "service":     self.service,
            "duration_ms": self.duration_ms,
            "tags":        self.tags,
            "logs":        self.logs,
            "error":       self.error,
        }


class DistributedTracer:
    MAX_TRACES = 1000
    _local     = threading.local()

    def __init__(self):
        self._traces: dict[str, list[DistributedSpan]] = {}
        self._lock   = threading.Lock()

    def current_context(self) -> SpanContext | None:
        return getattr(self._local, "ctx", None)

    def set_context(self, ctx: SpanContext) -> None:
        self._local.ctx = ctx

    @contextmanager
    def start_span(self, name: str, service: str = "wbs",
                   parent_ctx: SpanContext | None = None):
        parent = parent_ctx or self.current_context()
        ctx    = parent.child() if parent else SpanContext(
            trace_id=uuid.uuid4().hex[:16], span_id=uuid.uuid4().hex[:8]
        )
        span = DistributedSpan(ctx=ctx, name=name, service=service)
        prev = self.current_context()
        self.set_context(ctx)
        try:
            yield span
        except Exception as e:
            span.finish(error=str(e))
            raise
        finally:
            span.finish()
            self._record(span)
            self.set_context(prev)

    def _record(self, span: DistributedSpan) -> None:
        with self._lock:
            if len(self._traces) >= self.MAX_TRACES:
                oldest = next(iter(self._traces))
                del self._traces[oldest]
            self._traces.setdefault(span.ctx.trace_id, []).append(span)

    def get_trace(self, trace_id: str) -> list[dict]:
        with self._lock:
            return [s.to_dict() for s in self._traces.get(trace_id, [])]

    def get_recent_traces(self, limit: int = 20) -> list[dict]:
        with self._lock:
            result = []
            for tid, spans in list(self._traces.items())[-limit:]:
                result.append({
                    "trace_id":  tid,
                    "spans":     len(spans),
                    "services":  list({s.service for s in spans}),
                    "total_ms":  sum(s.duration_ms for s in spans),
                    "has_error": any(s.error for s in spans),
                })
            return result


distributed_tracer = DistributedTracer()
