"""
security/api_keys.py — API key system.

Keys are stored as HMAC-SHA256 hashes. The raw key is shown once on creation.
Format: wbs_<random_32_hex>

Scopes: read, write, publish, admin
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Any


KEY_PREFIX = "wbs_"
_HMAC_SECRET = b"wbs-api-key-hmac-secret"   # override via env in production


def _hash_key(raw_key: str) -> str:
    return hmac.new(_HMAC_SECRET, raw_key.encode(), hashlib.sha256).hexdigest()


def generate_key() -> tuple[str, str]:
    """Return (raw_key, key_hash). Store only the hash."""
    raw  = KEY_PREFIX + secrets.token_hex(32)
    return raw, _hash_key(raw)


def create_api_key(conn: sqlite3.Connection, user_id: str, org_id: str,
                   name: str, scopes: list[str],
                   expires_days: int | None = None) -> dict:
    import uuid, json
    raw, key_hash = generate_key()
    kid     = str(uuid.uuid4())
    now     = datetime.now(timezone.utc).isoformat()
    expires = None
    if expires_days:
        expires = (datetime.now(timezone.utc) + timedelta(days=expires_days)).isoformat()
    conn.execute(
        "INSERT INTO api_keys (id,user_id,org_id,key_hash,name,scopes,expires_at,created_at) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (kid, user_id, org_id, key_hash, name, json.dumps(scopes), expires, now)
    )
    conn.commit()
    return {"id": kid, "key": raw, "name": name, "scopes": scopes, "expires_at": expires}


def verify_api_key(conn: sqlite3.Connection, raw_key: str) -> dict | None:
    """Return the API key row if valid and not expired, else None."""
    import json
    if not raw_key.startswith(KEY_PREFIX):
        return None
    key_hash = _hash_key(raw_key)
    row = conn.execute(
        "SELECT * FROM api_keys WHERE key_hash=?", (key_hash,)
    ).fetchone()
    if not row:
        return None
    d = dict(row)
    if d.get("expires_at") and d["expires_at"] < datetime.now(timezone.utc).isoformat():
        return None
    # Update last_used
    conn.execute("UPDATE api_keys SET last_used=? WHERE id=?",
                 (datetime.now(timezone.utc).isoformat(), d["id"]))
    conn.commit()
    d["scopes"] = json.loads(d.get("scopes") or "[]")
    return d


def revoke_api_key(conn: sqlite3.Connection, key_id: str, user_id: str) -> bool:
    n = conn.execute(
        "DELETE FROM api_keys WHERE id=? AND user_id=?", (key_id, user_id)
    ).rowcount
    conn.commit()
    return n > 0


def list_api_keys(conn: sqlite3.Connection, user_id: str) -> list[dict]:
    import json
    rows = conn.execute(
        "SELECT id,name,scopes,last_used,expires_at,created_at FROM api_keys WHERE user_id=?",
        (user_id,)
    ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["scopes"] = json.loads(d.get("scopes") or "[]")
        result.append(d)
    return result
