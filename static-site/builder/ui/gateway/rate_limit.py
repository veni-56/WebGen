"""
gateway/rate_limit.py — Centralized rate limiting for the API gateway.

Token bucket algorithm, per-IP and per-user.
Configurable per route group.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from functools import wraps
from typing import Callable

from flask import g, jsonify, request


@dataclass
class Bucket:
    capacity:    float
    refill_rate: float   # tokens per second
    tokens:      float   = field(init=False)
    last_refill: float   = field(default_factory=time.monotonic)

    def __post_init__(self):
        self.tokens = self.capacity

    def consume(self, n: float = 1.0) -> bool:
        now     = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens     = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        if self.tokens >= n:
            self.tokens -= n
            return True
        return False


class RateLimiter:
    def __init__(self):
        self._buckets: dict[str, Bucket] = {}
        self._lock    = threading.Lock()

    def check(self, key: str, capacity: float = 60,
              per_minute: float = 60) -> bool:
        rate = per_minute / 60.0
        with self._lock:
            if key not in self._buckets:
                self._buckets[key] = Bucket(capacity=capacity, refill_rate=rate)
            return self._buckets[key].consume()

    def reset(self, key: str) -> None:
        with self._lock:
            self._buckets.pop(key, None)

    def stats(self) -> dict:
        with self._lock:
            return {k: round(b.tokens, 2) for k, b in self._buckets.items()}


# Singleton
limiter = RateLimiter()


def rate_limit(capacity: int = 60, per_minute: int = 60,
               key_fn: Callable | None = None):
    """
    Decorator: apply rate limiting to a Flask route.
    key_fn(request) → str  (default: IP address)
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = key_fn(request) if key_fn else request.remote_addr
            uid = getattr(g, "user_id", None)
            if uid:
                key = f"user:{uid}:{fn.__name__}"
            else:
                key = f"ip:{key}:{fn.__name__}"

            if not limiter.check(key, capacity, per_minute):
                return jsonify({
                    "success": False,
                    "error":   "Rate limit exceeded. Try again shortly.",
                    "data":    {},
                }), 429
            return fn(*args, **kwargs)
        return wrapper
    return decorator
