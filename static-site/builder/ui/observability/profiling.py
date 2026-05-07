"""
observability/profiling.py — Build flamegraph and performance profiling.

Captures timing data for build stages and generates a simple
flamegraph-compatible JSON output (compatible with speedscope.app).
"""
from __future__ import annotations

import json
import time
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProfileFrame:
    name:      str
    start_ms:  float
    end_ms:    float = 0.0
    children:  list  = field(default_factory=list)
    meta:      dict  = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        return round(self.end_ms - self.start_ms, 2)

    def finish(self) -> None:
        self.end_ms = time.time() * 1000

    def to_dict(self) -> dict:
        return {
            "name":        self.name,
            "duration_ms": self.duration_ms,
            "start_ms":    round(self.start_ms, 2),
            "end_ms":      round(self.end_ms, 2),
            "meta":        self.meta,
            "children":    [c.to_dict() for c in self.children],
        }


class BuildProfiler:
    """
    Records a hierarchical profile of a build run.
    Thread-local stack tracks nesting.
    """

    def __init__(self, build_id: str):
        self.build_id = build_id
        self._root    = ProfileFrame(name="build", start_ms=time.time() * 1000)
        self._stack   = [self._root]
        self._lock    = threading.Lock()

    @contextmanager
    def frame(self, name: str, **meta):
        f = ProfileFrame(name=name, start_ms=time.time() * 1000, meta=meta)
        with self._lock:
            self._stack[-1].children.append(f)
            self._stack.append(f)
        try:
            yield f
        finally:
            f.finish()
            with self._lock:
                if len(self._stack) > 1:
                    self._stack.pop()

    def finish(self) -> None:
        self._root.finish()

    def to_dict(self) -> dict:
        return {
            "build_id":    self.build_id,
            "total_ms":    self._root.duration_ms,
            "profile":     self._root.to_dict(),
        }

    def to_speedscope(self) -> dict:
        """
        Export in speedscope JSON format for flamegraph visualization.
        https://www.speedscope.app/
        """
        frames: list[dict] = []
        events: list[dict] = []

        def _walk(node: ProfileFrame) -> None:
            idx = len(frames)
            frames.append({"name": node.name})
            events.append({"type": "O", "frame": idx, "at": node.start_ms})
            for child in node.children:
                _walk(child)
            events.append({"type": "C", "frame": idx, "at": node.end_ms})

        _walk(self._root)

        return {
            "$schema":  "https://www.speedscope.app/file-format-schema.json",
            "version":  "0.0.1",
            "profiles": [{
                "type":       "evented",
                "name":       f"build:{self.build_id}",
                "unit":       "milliseconds",
                "startValue": self._root.start_ms,
                "endValue":   self._root.end_ms,
                "events":     events,
            }],
            "shared": {"frames": frames},
        }


# ── Global profiler registry ──────────────────────────────────────────────────

_profilers: dict[str, BuildProfiler] = {}
_MAX_PROFILERS = 50


def start_profile(build_id: str) -> BuildProfiler:
    p = BuildProfiler(build_id)
    if len(_profilers) >= _MAX_PROFILERS:
        oldest = next(iter(_profilers))
        del _profilers[oldest]
    _profilers[build_id] = p
    return p


def get_profile(build_id: str) -> BuildProfiler | None:
    return _profilers.get(build_id)


def list_profiles(limit: int = 20) -> list[dict]:
    return [
        {"build_id": bid, "total_ms": p._root.duration_ms}
        for bid, p in list(_profilers.items())[-limit:]
    ]
