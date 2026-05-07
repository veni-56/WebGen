"""
collab/sync.py — State sync engine.

Combines OT, presence, and sessions into a single sync API.
The server calls these functions from REST endpoints.

Flow:
  1. Client opens session → POST /api/v1/collab/<doc_id>/session
  2. Client sends ops    → POST /api/v1/collab/<doc_id>/ops
  3. Client polls ops    → GET  /api/v1/collab/<doc_id>/ops?since=<seq>
  4. Client pings        → POST /api/v1/collab/<doc_id>/ping
  5. Client leaves       → DELETE /api/v1/collab/<doc_id>/session/<sid>
"""
from __future__ import annotations

import copy
import threading
from typing import Any

from collab.operational_transform import OperationLog, apply_op, transform
from collab.presence import presence_store
from collab.sessions import session_store


# ── Per-document state ────────────────────────────────────────────────────────

class DocState:
    def __init__(self, doc_id: str, initial_state: dict):
        self.doc_id  = doc_id
        self._lock   = threading.Lock()
        self._state  = copy.deepcopy(initial_state)
        self._log    = OperationLog(doc_id)
        self._snapshots: list[dict] = []   # periodic checkpoints

    def apply_ops(self, ops: list[dict], user_id: str) -> tuple[list[dict], dict]:
        """
        Apply a list of ops from a client.
        Returns (applied_ops_with_seq, new_state).
        """
        with self._lock:
            applied = []
            for op in ops:
                entry = self._log.append(op, user_id)
                self._state = apply_op(self._state, op)
                applied.append(entry)
            return applied, copy.deepcopy(self._state)

    def get_ops_since(self, seq: int) -> list[dict]:
        with self._lock:
            return self._log.since(seq)

    def snapshot(self) -> dict:
        with self._lock:
            snap = {"seq": self._log._seq, "state": copy.deepcopy(self._state)}
            self._snapshots.append(snap)
            if len(self._snapshots) > 20:
                self._snapshots.pop(0)
            return snap

    def rollback_to(self, seq: int) -> dict | None:
        """Rollback to the nearest snapshot at or before seq."""
        with self._lock:
            candidates = [s for s in self._snapshots if s["seq"] <= seq]
            if not candidates:
                return None
            snap = max(candidates, key=lambda s: s["seq"])
            self._state = copy.deepcopy(snap["state"])
            self._log.clear_before(snap["seq"])
            return copy.deepcopy(self._state)

    def current_state(self) -> dict:
        with self._lock:
            return copy.deepcopy(self._state)


# ── Doc registry ──────────────────────────────────────────────────────────────

_docs_lock = threading.Lock()
_docs: dict[str, DocState] = {}


def get_or_create_doc(doc_id: str, initial_state: dict) -> DocState:
    with _docs_lock:
        if doc_id not in _docs:
            _docs[doc_id] = DocState(doc_id, initial_state)
        return _docs[doc_id]


def evict_doc(doc_id: str) -> None:
    with _docs_lock:
        _docs.pop(doc_id, None)


# ── Public sync API ───────────────────────────────────────────────────────────

def open_session(doc_id: str, user_id: str, org_id: str,
                 email: str = "", initial_state: dict | None = None) -> dict:
    """Open a collab session. Returns session info."""
    get_or_create_doc(doc_id, initial_state or {})
    session = session_store.create(doc_id, user_id, org_id)
    presence_store.update(doc_id, user_id, email=email)
    return session.to_dict()


def close_session(session_id: str, doc_id: str, user_id: str) -> None:
    session_store.close(session_id)
    presence_store.leave(doc_id, user_id)


def submit_ops(doc_id: str, user_id: str, ops: list[dict],
               client_seq: int = 0) -> dict:
    """
    Accept ops from a client, transform against any concurrent ops,
    apply, and return the server-assigned sequence numbers.
    """
    doc = _docs.get(doc_id)
    if doc is None:
        return {"error": "Document not found", "ok": False}

    # Transform incoming ops against any ops the client hasn't seen yet
    server_ops = doc.get_ops_since(client_seq)
    transformed = list(ops)
    for sop in server_ops:
        transformed = [transform(cop, sop) for cop in transformed]

    applied, new_state = doc.apply_ops(transformed, user_id)
    return {"ok": True, "ops": applied, "seq": doc._log._seq}


def get_ops_since(doc_id: str, seq: int) -> dict:
    doc = _docs.get(doc_id)
    if doc is None:
        return {"ops": [], "seq": 0}
    ops = doc.get_ops_since(seq)
    return {"ops": ops, "seq": doc._log._seq}


def ping_session(session_id: str, doc_id: str, user_id: str,
                 seq: int | None = None, cursor_block: str = "",
                 cursor_page: str = "") -> bool:
    ok = session_store.ping(session_id, seq)
    if ok:
        presence_store.update(doc_id, user_id,
                              cursor_block=cursor_block,
                              cursor_page=cursor_page)
    return ok


def get_presence(doc_id: str) -> list[dict]:
    return presence_store.get_for_doc(doc_id)
