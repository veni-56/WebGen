"""
collab/presence.py — Live presence tracking for collaborative editing.

Tracks which users are currently editing which documents (projects).
Stores cursor position, selected block, and last-seen timestamp.
No WebSocket required — presence is polled via REST.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field, asdict
from typing import Any


PRESENCE_TTL = 30   # seconds before a presence entry expires


@dataclass
class PresenceEntry:
    user_id:      str
    doc_id:       str
    email:        str        = ""
    cursor_block: str        = ""   # selected block ID
    cursor_page:  str        = ""   # active page key
    meta:         dict       = field(default_factory=dict)
    last_seen:    float      = field(default_factory=time.time)

    def is_alive(self) -> bool:
        return (time.time() - self.last_seen) < PRESENCE_TTL

    def to_dict(self) -> dict:
        d = asdict(self)
        d["last_seen_ago"] = round(time.time() - self.last_seen, 1)
        return d


class PresenceStore:
    """
    Thread-safe in-memory presence store.
    Key: (doc_id, user_id)
    """

    def __init__(self):
        self._lock    = threading.Lock()
        self._entries: dict[tuple[str, str], PresenceEntry] = {}

    def update(self, doc_id: str, user_id: str, email: str = "",
               cursor_block: str = "", cursor_page: str = "",
               meta: dict | None = None) -> PresenceEntry:
        key = (doc_id, user_id)
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                entry = PresenceEntry(user_id=user_id, doc_id=doc_id)
                self._entries[key] = entry
            entry.email        = email or entry.email
            entry.cursor_block = cursor_block or entry.cursor_block
            entry.cursor_page  = cursor_page  or entry.cursor_page
            entry.meta         = meta or entry.meta
            entry.last_seen    = time.time()
        return entry

    def leave(self, doc_id: str, user_id: str) -> None:
        with self._lock:
            self._entries.pop((doc_id, user_id), None)

    def get_for_doc(self, doc_id: str) -> list[dict]:
        with self._lock:
            self._prune()
            return [
                e.to_dict()
                for (did, _), e in self._entries.items()
                if did == doc_id and e.is_alive()
            ]

    def get_for_user(self, user_id: str) -> list[dict]:
        with self._lock:
            self._prune()
            return [
                e.to_dict()
                for (_, uid), e in self._entries.items()
                if uid == user_id and e.is_alive()
            ]

    def active_doc_count(self) -> int:
        with self._lock:
            self._prune()
            return len({did for (did, _) in self._entries})

    def _prune(self) -> None:
        """Remove stale entries. Must be called under _lock."""
        stale = [k for k, e in self._entries.items() if not e.is_alive()]
        for k in stale:
            del self._entries[k]


# Singleton
presence_store = PresenceStore()
