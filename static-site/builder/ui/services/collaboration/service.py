"""services/collaboration/service.py — Collaboration domain service."""
from __future__ import annotations
from services.base import BaseService


class CollaborationService(BaseService):
    service_name = "collaboration"

    def open_session(self, doc_id: str, user_id: str,
                     org_id: str, email: str = "",
                     initial_state: dict | None = None) -> dict:
        from collab.sync import open_session
        sess = open_session(doc_id, user_id, org_id, email, initial_state)
        self._emit("collab.session_opened", {"doc_id": doc_id, "user_id": user_id})
        return sess

    def submit_ops(self, doc_id: str, user_id: str,
                   ops: list[dict], client_seq: int = 0) -> dict:
        from collab.sync import submit_ops
        return submit_ops(doc_id, user_id, ops, client_seq)

    def get_presence(self, doc_id: str) -> list[dict]:
        from collab.sync import get_presence
        return get_presence(doc_id)

    def close_session(self, session_id: str, doc_id: str, user_id: str) -> None:
        from collab.sync import close_session
        close_session(session_id, doc_id, user_id)
        self._emit("collab.session_closed", {"doc_id": doc_id, "user_id": user_id})
