"""
collab/operational_transform.py — Operational Transform engine for config state.

Implements a simple last-write-wins OT for JSON path operations.
Operations are immutable dicts; the engine transforms them against
concurrent operations to produce a consistent final state.

Operation types:
  set    { op:'set',    path:'pages.home.title', value:'...' }
  delete { op:'delete', path:'pages.home' }
  insert { op:'insert', path:'pages.home.sections', index:2, value:'hero' }
  remove { op:'remove', path:'pages.home.sections', index:2 }
  move   { op:'move',   path:'pages.home.sections', from_idx:1, to_idx:3 }
"""
from __future__ import annotations

import copy
import json
from typing import Any


# ── Path helpers ──────────────────────────────────────────────────────────────

def _get(obj: Any, path: str) -> Any:
    parts = path.split(".")
    for p in parts:
        if isinstance(obj, dict):
            obj = obj.get(p)
        elif isinstance(obj, list):
            try:
                obj = obj[int(p)]
            except (ValueError, IndexError):
                return None
        else:
            return None
    return obj


def _set(obj: Any, path: str, value: Any) -> Any:
    """Return a new object with path set to value (immutable)."""
    obj = copy.deepcopy(obj)
    parts = path.split(".")
    node = obj
    for p in parts[:-1]:
        if isinstance(node, dict):
            if p not in node:
                node[p] = {}
            node = node[p]
        elif isinstance(node, list):
            node = node[int(p)]
    last = parts[-1]
    if isinstance(node, dict):
        node[last] = value
    elif isinstance(node, list):
        node[int(last)] = value
    return obj


def _delete(obj: Any, path: str) -> Any:
    obj = copy.deepcopy(obj)
    parts = path.split(".")
    node = obj
    for p in parts[:-1]:
        if isinstance(node, dict):
            node = node.get(p, {})
        elif isinstance(node, list):
            node = node[int(p)]
    last = parts[-1]
    if isinstance(node, dict):
        node.pop(last, None)
    elif isinstance(node, list):
        try:
            del node[int(last)]
        except (ValueError, IndexError):
            pass
    return obj


# ── Operation application ─────────────────────────────────────────────────────

def apply_op(state: dict, op: dict) -> dict:
    """Apply a single operation to state. Returns new state (immutable)."""
    kind  = op.get("op")
    path  = op.get("path", "")
    value = op.get("value")

    if kind == "set":
        return _set(state, path, value)

    if kind == "delete":
        return _delete(state, path)

    if kind == "insert":
        state = copy.deepcopy(state)
        lst   = _get(state, path)
        if isinstance(lst, list):
            idx = min(op.get("index", len(lst)), len(lst))
            lst.insert(idx, value)
        return state

    if kind == "remove":
        state = copy.deepcopy(state)
        lst   = _get(state, path)
        if isinstance(lst, list):
            idx = op.get("index", -1)
            if 0 <= idx < len(lst):
                lst.pop(idx)
        return state

    if kind == "move":
        state    = copy.deepcopy(state)
        lst      = _get(state, path)
        from_idx = op.get("from_idx", 0)
        to_idx   = op.get("to_idx", 0)
        if isinstance(lst, list) and 0 <= from_idx < len(lst):
            item = lst.pop(from_idx)
            to_idx = min(to_idx, len(lst))
            lst.insert(to_idx, item)
        return state

    # Unknown op — return state unchanged
    return state


# ── Transform (OT) ────────────────────────────────────────────────────────────

def transform(op_a: dict, op_b: dict) -> dict:
    """
    Transform op_a against concurrent op_b.
    Returns a new op_a' that can be applied after op_b.

    Simple last-write-wins for 'set' conflicts on the same path.
    Index-shift for list operations.
    """
    if op_a.get("path") != op_b.get("path"):
        return op_a   # different paths — no conflict

    kind_a = op_a.get("op")
    kind_b = op_b.get("op")

    # set vs set on same path → last writer wins (op_b already applied)
    if kind_a == "set" and kind_b == "set":
        return op_a   # caller decides ordering; here we keep op_a

    # insert/remove index shifting
    if kind_a in ("insert", "remove") and kind_b in ("insert", "remove"):
        idx_a = op_a.get("index", 0)
        idx_b = op_b.get("index", 0)
        new_op = dict(op_a)
        if kind_b == "insert" and idx_b <= idx_a:
            new_op["index"] = idx_a + 1
        elif kind_b == "remove" and idx_b < idx_a:
            new_op["index"] = max(0, idx_a - 1)
        return new_op

    return op_a


# ── Operation log ─────────────────────────────────────────────────────────────

class OperationLog:
    """
    In-memory append-only log of operations for a single document (project).
    Supports replay and checkpoint.
    """

    def __init__(self, doc_id: str):
        self.doc_id  = doc_id
        self._ops:   list[dict] = []
        self._seq    = 0

    def append(self, op: dict, user_id: str = "") -> dict:
        self._seq += 1
        entry = {**op, "seq": self._seq, "user_id": user_id}
        self._ops.append(entry)
        return entry

    def since(self, seq: int) -> list[dict]:
        return [o for o in self._ops if o["seq"] > seq]

    def replay(self, base_state: dict, from_seq: int = 0) -> dict:
        state = copy.deepcopy(base_state)
        for op in self._ops:
            if op["seq"] > from_seq:
                state = apply_op(state, op)
        return state

    def checkpoint(self) -> dict:
        return {"doc_id": self.doc_id, "seq": self._seq, "op_count": len(self._ops)}

    def clear_before(self, seq: int) -> None:
        self._ops = [o for o in self._ops if o["seq"] >= seq]
