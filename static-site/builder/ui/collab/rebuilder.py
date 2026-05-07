"""
collab/rebuilder.py — State rebuilder for incremental sync.

Rebuilds document state from a snapshot + op log.
Generates incremental sync tokens so clients only receive
ops they haven't seen yet.
"""
from __future__ import annotations

import base64
import hashlib
import json
import time
from typing import Any


class SyncToken:
    """Opaque token encoding the client's last-known seq + doc fingerprint."""

    def __init__(self, doc_id: str, seq: int, ts: float | None = None):
        self.doc_id = doc_id
        self.seq    = seq
        self.ts     = ts or time.time()

    def encode(self) -> str:
        data = json.dumps({"d": self.doc_id, "s": self.seq, "t": round(self.ts)})
        return base64.urlsafe_b64encode(data.encode()).decode()

    @classmethod
    def decode(cls, token: str) -> "SyncToken | None":
        try:
            data = json.loads(base64.urlsafe_b64decode(token.encode()))
            return cls(doc_id=data["d"], seq=data["s"], ts=data.get("t", 0))
        except Exception:
            return None


class StateRebuilder:
    """
    Rebuilds document state efficiently using snapshots + op replay.
    """

    def rebuild(self, doc_id: str, snapshot_store,
                op_log, target_seq: int | None = None) -> dict:
        """
        Rebuild state at target_seq (or latest if None).
        Uses nearest snapshot + replay of ops since that snapshot.
        """
        from collab.operational_transform import apply_op
        import copy

        # Find best snapshot
        snap = snapshot_store.get_latest(doc_id) if target_seq is None \
               else snapshot_store.get_at_or_before(doc_id, target_seq or 0)

        if snap:
            state    = copy.deepcopy(snap["state"])
            from_seq = snap["seq"]
        else:
            state    = {}
            from_seq = 0

        # Replay ops since snapshot
        ops = op_log.since(from_seq)
        if target_seq is not None:
            ops = [o for o in ops if o["seq"] <= target_seq]

        for op in ops:
            state = apply_op(state, op)

        return state

    def incremental_sync(self, doc_id: str, token: str | None,
                         op_log) -> dict:
        """
        Return ops the client hasn't seen yet, plus a new sync token.
        """
        if token:
            st = SyncToken.decode(token)
            since_seq = st.seq if st and st.doc_id == doc_id else 0
        else:
            since_seq = 0

        ops      = op_log.since(since_seq)
        new_seq  = op_log._seq
        new_token = SyncToken(doc_id, new_seq).encode()

        return {
            "ops":       ops,
            "seq":       new_seq,
            "token":     new_token,
            "has_more":  False,
        }

    def fingerprint(self, state: dict) -> str:
        """Stable fingerprint of a state dict for cache validation."""
        canonical = json.dumps(state, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]


rebuilder = StateRebuilder()
