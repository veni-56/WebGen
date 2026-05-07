"""
collab/sessions.py — Collaboration session management.

A session represents one user's editing connection to one document.
Sessions are short-lived (TTL = 2 hours) and stored in-memory.
They carry the user's last-known sequence number for OT sync.
"""
from __future__ import annotations

import secrets
import threading
import time
from dataclasses import dataclass, field


SESSION_TTL = 7200   # 2 hours


@dataclass
class CollabSession:
    session_id: str
    doc_id:     str
    user_id:    str
    org_id:     str
    last_seq:   int   = 0       # last OT sequence number seen by this client
    created_at: float = field(default_factory=time.time)
    last_ping:  float = field(default_factory=time.time)

    def is_alive(self) -> bool:
        return (time.time() - self.last_ping) < SESSION_TTL

    def ping(self, seq: int | None = None) -> None:
        self.last_ping = time.time()
        if seq is not None:
            self.last_seq = seq

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "doc_id":     self.doc_id,
            "user_id":    self.user_id,
            "org_id":     self.org_id,
            "last_seq":   self.last_seq,
            "age_s":      round(time.time() - self.created_at),
        }


class SessionStore:
    def __init__(self):
        self._lock     = threading.Lock()
        self._sessions: dict[str, CollabSession] = {}

    def create(self, doc_id: str, user_id: str, org_id: str) -> CollabSession:
        sid     = secrets.token_urlsafe(16)
        session = CollabSession(session_id=sid, doc_id=doc_id,
                                user_id=user_id, org_id=org_id)
        with self._lock:
            self._sessions[sid] = session
        return session

    def get(self, session_id: str) -> CollabSession | None:
        with self._lock:
            s = self._sessions.get(session_id)
            return s if s and s.is_alive() else None

    def ping(self, session_id: str, seq: int | None = None) -> bool:
        with self._lock:
            s = self._sessions.get(session_id)
            if s and s.is_alive():
                s.ping(seq)
                return True
            return False

    def close(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def list_for_doc(self, doc_id: str) -> list[dict]:
        with self._lock:
            self._prune()
            return [s.to_dict() for s in self._sessions.values()
                    if s.doc_id == doc_id and s.is_alive()]

    def _prune(self) -> None:
        stale = [sid for sid, s in self._sessions.items() if not s.is_alive()]
        for sid in stale:
            del self._sessions[sid]


session_store = SessionStore()
