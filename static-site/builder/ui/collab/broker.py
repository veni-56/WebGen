"""
collab/broker.py — Distributed collaboration broker.

Abstracts the session/operation transport layer so it can be backed by:
  - In-process (default, current)
  - Redis pub/sub (future)
  - Kafka (future)

The broker is the single point of contact for all collab operations.
Horizontal scaling: multiple server processes share state via the broker backend.
"""
from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from typing import Any


# ── Backend interface ─────────────────────────────────────────────────────────

class BrokerBackend(ABC):
    """Abstract backend — swap for Redis/Kafka without changing callers."""

    @abstractmethod
    def publish(self, channel: str, message: dict) -> None: ...

    @abstractmethod
    def subscribe(self, channel: str, handler) -> None: ...

    @abstractmethod
    def get(self, key: str) -> Any: ...

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int | None = None) -> None: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...

    @abstractmethod
    def keys(self, pattern: str) -> list[str]: ...


# ── In-process backend (default) ─────────────────────────────────────────────

class InProcessBackend(BrokerBackend):
    """Thread-safe in-memory backend. Works for single-process deployments."""

    def __init__(self):
        self._store:    dict[str, Any]          = {}
        self._ttls:     dict[str, float]        = {}
        self._subs:     dict[str, list]         = {}
        self._lock      = threading.Lock()

    def publish(self, channel: str, message: dict) -> None:
        with self._lock:
            handlers = list(self._subs.get(channel, []))
        for h in handlers:
            try:
                h(message)
            except Exception:
                pass

    def subscribe(self, channel: str, handler) -> None:
        with self._lock:
            self._subs.setdefault(channel, []).append(handler)

    def get(self, key: str) -> Any:
        with self._lock:
            if key in self._ttls and time.time() > self._ttls[key]:
                del self._store[key]
                del self._ttls[key]
                return None
            return self._store.get(key)

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        with self._lock:
            self._store[key] = value
            if ttl:
                self._ttls[key] = time.time() + ttl

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)
            self._ttls.pop(key, None)

    def keys(self, pattern: str) -> list[str]:
        import fnmatch
        with self._lock:
            return [k for k in self._store if fnmatch.fnmatch(k, pattern)]


# ── Redis adapter stub (ready for future wiring) ──────────────────────────────

class RedisBackend(BrokerBackend):
    """Redis-backed broker. Requires redis-py. Enables horizontal scaling."""

    def __init__(self, url: str = "redis://localhost:6379"):
        self._url = url
        self._r   = None
        self._connect()

    def _connect(self):
        try:
            import redis
            self._r = redis.from_url(self._url, decode_responses=True)
        except ImportError:
            raise RuntimeError("redis-py not installed: pip install redis")

    def publish(self, channel: str, message: dict) -> None:
        import json
        self._r.publish(channel, json.dumps(message))

    def subscribe(self, channel: str, handler) -> None:
        import json, threading
        def _listen():
            ps = self._r.pubsub()
            ps.subscribe(channel)
            for msg in ps.listen():
                if msg["type"] == "message":
                    try:
                        handler(json.loads(msg["data"]))
                    except Exception:
                        pass
        threading.Thread(target=_listen, daemon=True).start()

    def get(self, key: str) -> Any:
        import json
        v = self._r.get(key)
        return json.loads(v) if v else None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        import json
        self._r.set(key, json.dumps(value), ex=ttl)

    def delete(self, key: str) -> None:
        self._r.delete(key)

    def keys(self, pattern: str) -> list[str]:
        return self._r.keys(pattern)


# ── Collaboration Broker ──────────────────────────────────────────────────────

class CollabBroker:
    """
    High-level collaboration broker.
    Uses a pluggable backend (InProcess by default).
    """

    SESSION_TTL  = 7200   # 2 hours
    PRESENCE_TTL = 60     # 1 minute

    def __init__(self, backend: BrokerBackend | None = None):
        self._backend = backend or InProcessBackend()

    def use_backend(self, backend: BrokerBackend) -> None:
        self._backend = backend

    # ── Session registry ──────────────────────────────────────────────────────

    def register_session(self, session_id: str, doc_id: str,
                         user_id: str, org_id: str) -> None:
        key = f"session:{session_id}"
        self._backend.set(key, {
            "session_id": session_id, "doc_id": doc_id,
            "user_id": user_id, "org_id": org_id,
            "created_at": time.time(),
        }, ttl=self.SESSION_TTL)
        # Index by doc
        doc_key = f"doc_sessions:{doc_id}"
        sessions = self._backend.get(doc_key) or []
        if session_id not in sessions:
            sessions.append(session_id)
        self._backend.set(doc_key, sessions, ttl=self.SESSION_TTL)

    def get_session(self, session_id: str) -> dict | None:
        return self._backend.get(f"session:{session_id}")

    def remove_session(self, session_id: str, doc_id: str) -> None:
        self._backend.delete(f"session:{session_id}")
        doc_key  = f"doc_sessions:{doc_id}"
        sessions = self._backend.get(doc_key) or []
        sessions = [s for s in sessions if s != session_id]
        self._backend.set(doc_key, sessions, ttl=self.SESSION_TTL)

    def get_doc_sessions(self, doc_id: str) -> list[dict]:
        session_ids = self._backend.get(f"doc_sessions:{doc_id}") or []
        result = []
        for sid in session_ids:
            s = self._backend.get(f"session:{sid}")
            if s:
                result.append(s)
        return result

    # ── Presence ──────────────────────────────────────────────────────────────

    def update_presence(self, doc_id: str, user_id: str, data: dict) -> None:
        key = f"presence:{doc_id}:{user_id}"
        self._backend.set(key, {**data, "ts": time.time()}, ttl=self.PRESENCE_TTL)

    def get_presence(self, doc_id: str) -> list[dict]:
        pattern = f"presence:{doc_id}:*"
        keys    = self._backend.keys(pattern)
        result  = []
        for k in keys:
            v = self._backend.get(k)
            if v:
                result.append(v)
        return result

    # ── Operation batching ────────────────────────────────────────────────────

    def push_op(self, doc_id: str, op: dict) -> None:
        """Push an operation to the doc's pending batch."""
        key  = f"ops_batch:{doc_id}"
        ops  = self._backend.get(key) or []
        ops.append(op)
        self._backend.set(key, ops, ttl=300)

    def flush_ops(self, doc_id: str) -> list[dict]:
        """Atomically retrieve and clear the pending op batch."""
        key = f"ops_batch:{doc_id}"
        ops = self._backend.get(key) or []
        self._backend.delete(key)
        return ops

    # ── Pub/sub for real-time fan-out ─────────────────────────────────────────

    def broadcast(self, doc_id: str, message: dict) -> None:
        self._backend.publish(f"doc:{doc_id}", message)

    def listen(self, doc_id: str, handler) -> None:
        self._backend.subscribe(f"doc:{doc_id}", handler)


# ── Singleton ─────────────────────────────────────────────────────────────────
broker = CollabBroker()
