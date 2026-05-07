"""
core/event_bus.py — Internal distributed event bus.

Features:
  - publish(event_type, payload, source)
  - subscribe(event_type, handler, group)
  - async queue processing (background thread)
  - per-handler retry with exponential backoff
  - dead-letter store for permanently failed events
  - event replay from persisted log
  - SQLite persistence (optional)

Usage:
    from core.event_bus import bus

    @bus.on("project.created")
    def handle_project_created(event):
        send_welcome_email(event["payload"]["user_id"])

    bus.publish("project.created", {"project_id": "abc", "user_id": "xyz"})
"""
from __future__ import annotations

import json
import queue
import sqlite3
import threading
import time
import traceback
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


# ── Event model ───────────────────────────────────────────────────────────────

@dataclass
class Event:
    id:         str   = field(default_factory=lambda: uuid.uuid4().hex[:16])
    type:       str   = ""
    payload:    dict  = field(default_factory=dict)
    source:     str   = "system"
    ts:         str   = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    attempt:    int   = 0
    correlation_id: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Event":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── Dead-letter store ─────────────────────────────────────────────────────────

@dataclass
class DeadLetter:
    event:   Event
    handler: str
    error:   str
    ts:      str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ── Event Bus ─────────────────────────────────────────────────────────────────

class EventBus:
    MAX_RETRIES    = 3
    BACKOFF_BASE   = 1.0
    QUEUE_MAXSIZE  = 2000
    PERSIST_LIMIT  = 10_000   # max events kept in SQLite

    def __init__(self):
        self._handlers:    dict[str, list[dict]]  = {}   # type → [{fn, group, name}]
        self._queue:       queue.Queue            = queue.Queue(maxsize=self.QUEUE_MAXSIZE)
        self._dead_letters: list[DeadLetter]      = []
        self._lock         = threading.Lock()
        self._stop         = threading.Event()
        self._thread:      threading.Thread | None = None
        self._db_path:     str | None              = None
        self._replay_log:  list[Event]             = []   # in-memory ring (last 500)

    # ── Configuration ─────────────────────────────────────────────────────────

    def configure(self, db_path: str | None = None) -> None:
        self._db_path = db_path
        if db_path:
            self._init_db(db_path)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._worker, daemon=True, name="event-bus")
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    # ── Subscribe ─────────────────────────────────────────────────────────────

    def on(self, event_type: str, group: str = "default"):
        """Decorator: @bus.on('project.created')"""
        def decorator(fn: Callable) -> Callable:
            self.subscribe(event_type, fn, group=group)
            return fn
        return decorator

    def subscribe(self, event_type: str, handler: Callable,
                  group: str = "default") -> None:
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            # Wildcard '*' handlers receive all events
            self._handlers[event_type].append({
                "fn":    handler,
                "group": group,
                "name":  getattr(handler, "__name__", str(handler)),
            })

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        with self._lock:
            if event_type in self._handlers:
                self._handlers[event_type] = [
                    h for h in self._handlers[event_type] if h["fn"] is not handler
                ]

    # ── Publish ───────────────────────────────────────────────────────────────

    def publish(self, event_type: str, payload: dict | None = None,
                source: str = "system", correlation_id: str = "") -> Event:
        event = Event(
            type=event_type,
            payload=payload or {},
            source=source,
            correlation_id=correlation_id,
        )
        # Persist to SQLite
        if self._db_path:
            self._persist(event)
        # Add to replay log
        self._replay_log.append(event)
        if len(self._replay_log) > 500:
            self._replay_log.pop(0)
        # Enqueue for async dispatch
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            # Drop oldest and retry
            try:
                self._queue.get_nowait()
                self._queue.put_nowait(event)
            except Exception:
                pass
        return event

    def publish_sync(self, event_type: str, payload: dict | None = None,
                     source: str = "system") -> Event:
        """Dispatch synchronously (blocks until all handlers complete)."""
        event = Event(type=event_type, payload=payload or {}, source=source)
        self._dispatch(event)
        return event

    # ── Replay ────────────────────────────────────────────────────────────────

    def replay(self, event_type: str | None = None,
               since_ts: str | None = None, limit: int = 100) -> list[Event]:
        """Replay events from the in-memory log or SQLite."""
        if self._db_path:
            return self._replay_from_db(event_type, since_ts, limit)
        events = self._replay_log
        if event_type:
            events = [e for e in events if e.type == event_type]
        if since_ts:
            events = [e for e in events if e.ts >= since_ts]
        return events[-limit:]

    def replay_and_dispatch(self, event_type: str | None = None,
                             since_ts: str | None = None) -> int:
        """Replay and re-dispatch events. Returns count dispatched."""
        events = self.replay(event_type, since_ts)
        for e in events:
            self._dispatch(e)
        return len(events)

    # ── Dead letters ──────────────────────────────────────────────────────────

    def get_dead_letters(self, limit: int = 50) -> list[dict]:
        return [
            {"event": dl.event.to_dict(), "handler": dl.handler,
             "error": dl.error, "ts": dl.ts}
            for dl in self._dead_letters[-limit:]
        ]

    def retry_dead_letter(self, event_id: str) -> bool:
        for dl in self._dead_letters:
            if dl.event.id == event_id:
                self._queue.put_nowait(dl.event)
                return True
        return False

    # ── Inspect ───────────────────────────────────────────────────────────────

    def inspect(self) -> dict:
        with self._lock:
            return {
                "subscriptions": {
                    t: [h["name"] for h in hs]
                    for t, hs in self._handlers.items()
                },
                "queue_size":    self._queue.qsize(),
                "dead_letters":  len(self._dead_letters),
                "replay_log":    len(self._replay_log),
            }

    # ── Internal ──────────────────────────────────────────────────────────────

    def _worker(self) -> None:
        while not self._stop.is_set():
            try:
                event = self._queue.get(timeout=0.5)
                self._dispatch(event)
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                pass

    def _dispatch(self, event: Event) -> None:
        with self._lock:
            handlers = list(self._handlers.get(event.type, []))
            handlers += list(self._handlers.get("*", []))

        for h in handlers:
            self._call_with_retry(event, h)

    def _call_with_retry(self, event: Event, handler: dict) -> None:
        fn   = handler["fn"]
        name = handler["name"]
        for attempt in range(self.MAX_RETRIES):
            try:
                fn(event.to_dict())
                return
            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.BACKOFF_BASE * (2 ** attempt))
                else:
                    self._dead_letters.append(DeadLetter(
                        event=event, handler=name,
                        error=f"{type(e).__name__}: {e}\n{traceback.format_exc()[-500:]}"
                    ))
                    if len(self._dead_letters) > 1000:
                        self._dead_letters.pop(0)

    def _init_db(self, db_path: str) -> None:
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS event_log (
                id             TEXT PRIMARY KEY,
                type           TEXT NOT NULL,
                payload        TEXT NOT NULL,
                source         TEXT NOT NULL,
                ts             TEXT NOT NULL,
                correlation_id TEXT NOT NULL DEFAULT ''
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_event_log_type ON event_log(type, ts)")
        conn.commit(); conn.close()

    def _persist(self, event: Event) -> None:
        try:
            conn = sqlite3.connect(self._db_path)
            conn.execute(
                "INSERT OR IGNORE INTO event_log (id,type,payload,source,ts,correlation_id) "
                "VALUES (?,?,?,?,?,?)",
                (event.id, event.type, json.dumps(event.payload),
                 event.source, event.ts, event.correlation_id)
            )
            # Prune old events
            conn.execute(f"""
                DELETE FROM event_log WHERE id NOT IN (
                    SELECT id FROM event_log ORDER BY ts DESC LIMIT {self.PERSIST_LIMIT}
                )
            """)
            conn.commit(); conn.close()
        except Exception:
            pass

    def _replay_from_db(self, event_type, since_ts, limit) -> list[Event]:
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            sql, params = "SELECT * FROM event_log WHERE 1=1", []
            if event_type:
                sql += " AND type=?"; params.append(event_type)
            if since_ts:
                sql += " AND ts>=?"; params.append(since_ts)
            sql += " ORDER BY ts DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(sql, params).fetchall()
            conn.close()
            return [Event(id=r["id"], type=r["type"],
                          payload=json.loads(r["payload"]),
                          source=r["source"], ts=r["ts"],
                          correlation_id=r["correlation_id"])
                    for r in rows]
        except Exception:
            return []


# ── Singleton ─────────────────────────────────────────────────────────────────
bus = EventBus()
