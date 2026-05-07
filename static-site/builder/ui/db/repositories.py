"""
Repository pattern for the Website Builder SaaS platform.

Each repository class accepts a ``sqlite3.Connection`` and exposes typed
methods for CRUD operations.  All SQL uses parameterized queries — no string
formatting is used to build SQL.

Conventions
-----------
- Row dicts are returned as plain ``dict`` objects (converted from
  ``sqlite3.Row``) so callers do not depend on the sqlite3 API.
- JSON columns (``config``, ``metadata``, ``scopes``) are automatically
  decoded on read and encoded on write.
- ``ValueError`` is raised when a required record is not found and the
  operation cannot proceed without it.
- All other ``sqlite3`` errors propagate to the caller unchanged.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


def _row_to_dict(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    return dict(row)


def _rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(r) for r in rows]


def _json_encode(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"))


def _parse_config(row: dict | None) -> dict | None:
    """Decode the ``config`` JSON field in a project row in-place."""
    if row is None:
        return None
    if "config" in row and isinstance(row["config"], str):
        try:
            row["config"] = json.loads(row["config"])
        except (json.JSONDecodeError, TypeError):
            row["config"] = {}
    return row


def _config_hash(config: Any) -> str:
    """Stable SHA-256 hash of a config value (serialised as sorted JSON)."""
    serialised = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialised.encode()).hexdigest()


# ---------------------------------------------------------------------------
# UserRepository
# ---------------------------------------------------------------------------

class UserRepository:
    """CRUD operations for the ``users`` table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    def find_by_id(self, uid: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM users WHERE id = ?", (uid,)
        ).fetchone()
        return _row_to_dict(row)

    def find_by_email(self, email: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        return _row_to_dict(row)

    def create(self, email: str, password_hash: str) -> str:
        uid = _new_id()
        self._conn.execute(
            "INSERT INTO users (id, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (uid, email, password_hash, _now()),
        )
        return uid

    def update(self, uid: str, **fields: Any) -> None:
        if not fields:
            return
        allowed = {"email", "password_hash"}
        invalid = set(fields) - allowed
        if invalid:
            raise ValueError(f"Invalid user fields: {invalid}")
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [uid]
        self._conn.execute(
            f"UPDATE users SET {set_clause} WHERE id = ?", values  # noqa: S608
        )

    def delete(self, uid: str) -> None:
        self._conn.execute("DELETE FROM users WHERE id = ?", (uid,))


# ---------------------------------------------------------------------------
# OrgRepository
# ---------------------------------------------------------------------------

class OrgRepository:
    """CRUD operations for ``organizations`` and ``org_members``."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    def find_by_id(self, org_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM organizations WHERE id = ?", (org_id,)
        ).fetchone()
        return _row_to_dict(row)

    def find_by_slug(self, slug: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM organizations WHERE slug = ?", (slug,)
        ).fetchone()
        return _row_to_dict(row)

    def create(self, name: str, slug: str, plan: str = "free") -> str:
        org_id = _new_id()
        self._conn.execute(
            "INSERT INTO organizations (id, name, slug, plan, created_at) VALUES (?, ?, ?, ?, ?)",
            (org_id, name, slug, plan, _now()),
        )
        return org_id

    def list_for_user(self, user_id: str) -> list[dict]:
        rows = self._conn.execute(
            """
            SELECT o.*, m.role
            FROM organizations o
            JOIN org_members m ON m.org_id = o.id
            WHERE m.user_id = ?
            ORDER BY o.name
            """,
            (user_id,),
        ).fetchall()
        return _rows_to_dicts(rows)

    # ------------------------------------------------------------------
    # Membership
    # ------------------------------------------------------------------

    def add_member(self, org_id: str, user_id: str, role: str) -> None:
        member_id = _new_id()
        self._conn.execute(
            """
            INSERT INTO org_members (id, org_id, user_id, role, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (member_id, org_id, user_id, role, _now()),
        )

    def get_member(self, org_id: str, user_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM org_members WHERE org_id = ? AND user_id = ?",
            (org_id, user_id),
        ).fetchone()
        return _row_to_dict(row)

    def update_member_role(self, org_id: str, user_id: str, role: str) -> None:
        self._conn.execute(
            "UPDATE org_members SET role = ? WHERE org_id = ? AND user_id = ?",
            (role, org_id, user_id),
        )

    def remove_member(self, org_id: str, user_id: str) -> None:
        self._conn.execute(
            "DELETE FROM org_members WHERE org_id = ? AND user_id = ?",
            (org_id, user_id),
        )

    def list_members(self, org_id: str) -> list[dict]:
        rows = self._conn.execute(
            """
            SELECT m.*, u.email
            FROM org_members m
            JOIN users u ON u.id = m.user_id
            WHERE m.org_id = ?
            ORDER BY m.created_at
            """,
            (org_id,),
        ).fetchall()
        return _rows_to_dicts(rows)


# ---------------------------------------------------------------------------
# WorkspaceRepository
# ---------------------------------------------------------------------------

class WorkspaceRepository:
    """CRUD operations for the ``workspaces`` table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def find_by_id(self, ws_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM workspaces WHERE id = ?", (ws_id,)
        ).fetchone()
        return _row_to_dict(row)

    def find_by_slug(self, org_id: str, slug: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM workspaces WHERE org_id = ? AND slug = ?",
            (org_id, slug),
        ).fetchone()
        return _row_to_dict(row)

    def create(self, org_id: str, name: str, slug: str) -> str:
        ws_id = _new_id()
        self._conn.execute(
            "INSERT INTO workspaces (id, org_id, name, slug, created_at) VALUES (?, ?, ?, ?, ?)",
            (ws_id, org_id, name, slug, _now()),
        )
        return ws_id

    def list_for_org(self, org_id: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM workspaces WHERE org_id = ? ORDER BY name",
            (org_id,),
        ).fetchall()
        return _rows_to_dicts(rows)

    def delete(self, ws_id: str) -> None:
        self._conn.execute("DELETE FROM workspaces WHERE id = ?", (ws_id,))


# ---------------------------------------------------------------------------
# ProjectRepository
# ---------------------------------------------------------------------------

class ProjectRepository:
    """CRUD operations for the ``projects`` table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    def find_by_id(self, pid: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM projects WHERE id = ?", (pid,)
        ).fetchone()
        return _parse_config(_row_to_dict(row))

    def find_by_slug(self, slug: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM projects WHERE slug = ?", (slug,)
        ).fetchone()
        return _parse_config(_row_to_dict(row))

    def list_for_workspace(self, ws_id: str, limit: int = 50) -> list[dict]:
        rows = self._conn.execute(
            """
            SELECT * FROM projects
            WHERE workspace_id = ?
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (ws_id, limit),
        ).fetchall()
        return [_parse_config(r) for r in _rows_to_dicts(rows)]  # type: ignore[misc]

    def list_for_user(self, user_id: str, limit: int = 50) -> list[dict]:
        rows = self._conn.execute(
            """
            SELECT * FROM projects
            WHERE user_id = ?
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        return [_parse_config(r) for r in _rows_to_dicts(rows)]  # type: ignore[misc]

    def create(
        self,
        user_id: str,
        org_id: str,
        ws_id: str | None,
        name: str,
        slug: str,
        config: Any,
    ) -> str:
        pid = _new_id()
        now = _now()
        config_str = _json_encode(config)
        chash = _config_hash(config)
        self._conn.execute(
            """
            INSERT INTO projects
                (id, org_id, workspace_id, user_id, name, slug,
                 config, config_hash, published, publish_url, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, '', ?, ?)
            """,
            (pid, org_id, ws_id, user_id, name, slug, config_str, chash, now, now),
        )
        return pid

    def update(self, pid: str, **fields: Any) -> bool:
        """
        Update project fields.

        If ``config`` is provided, it is serialised and its hash is computed.
        Returns ``False`` when a ``config`` update is attempted but the hash
        is identical to the stored value (no-op); returns ``True`` otherwise.
        """
        if not fields:
            return True

        allowed = {
            "name", "slug", "config", "published", "publish_url",
            "workspace_id", "org_id",
        }
        invalid = set(fields) - allowed
        if invalid:
            raise ValueError(f"Invalid project fields: {invalid}")

        # Handle config serialisation and hash check.
        if "config" in fields:
            new_config = fields.pop("config")
            new_hash = _config_hash(new_config)
            row = self._conn.execute(
                "SELECT config_hash FROM projects WHERE id = ?", (pid,)
            ).fetchone()
            if row is None:
                raise ValueError(f"Project not found: {pid}")
            if row["config_hash"] == new_hash:
                return False
            fields["config"] = _json_encode(new_config)
            fields["config_hash"] = new_hash

        fields["updated_at"] = _now()
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [pid]
        self._conn.execute(
            f"UPDATE projects SET {set_clause} WHERE id = ?", values  # noqa: S608
        )
        return True

    def delete(self, pid: str) -> None:
        self._conn.execute("DELETE FROM projects WHERE id = ?", (pid,))

    def duplicate(self, pid: str, new_name: str) -> str:
        """
        Clone an existing project under *new_name*.

        The new project gets a fresh id, a derived slug, and reset
        publish state.  Raises ``ValueError`` if the source project is
        not found.
        """
        source = self.find_by_id(pid)
        if source is None:
            raise ValueError(f"Project not found: {pid}")

        new_pid = _new_id()
        now = _now()
        # Derive a unique slug by appending the first 8 chars of the new id.
        new_slug = f"{source['slug']}-copy-{new_pid[:8]}"
        config_str = _json_encode(source.get("config", {}))
        chash = _config_hash(source.get("config", {}))

        self._conn.execute(
            """
            INSERT INTO projects
                (id, org_id, workspace_id, user_id, name, slug,
                 config, config_hash, published, publish_url, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, '', ?, ?)
            """,
            (
                new_pid,
                source["org_id"],
                source.get("workspace_id"),
                source["user_id"],
                new_name,
                new_slug,
                config_str,
                chash,
                now,
                now,
            ),
        )
        return new_pid


# ---------------------------------------------------------------------------
# AuditRepository
# ---------------------------------------------------------------------------

class AuditRepository:
    """Write and query the ``audit_logs`` table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def log(
        self,
        org_id: str | None,
        user_id: str | None,
        action: str,
        resource_type: str,
        resource_id: str,
        metadata: Any = None,
        ip: str | None = None,
    ) -> None:
        meta_str = _json_encode(metadata) if metadata is not None else None
        self._conn.execute(
            """
            INSERT INTO audit_logs
                (org_id, user_id, action, resource_type, resource_id,
                 metadata, ip, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (org_id, user_id, action, resource_type, resource_id,
             meta_str, ip, _now()),
        )

    def list_for_org(self, org_id: str, limit: int = 100) -> list[dict]:
        rows = self._conn.execute(
            """
            SELECT * FROM audit_logs
            WHERE org_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (org_id, limit),
        ).fetchall()
        return _rows_to_dicts(rows)

    def list_for_resource(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 50,
    ) -> list[dict]:
        rows = self._conn.execute(
            """
            SELECT * FROM audit_logs
            WHERE resource_type = ? AND resource_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (resource_type, resource_id, limit),
        ).fetchall()
        return _rows_to_dicts(rows)
