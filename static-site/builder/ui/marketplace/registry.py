"""
marketplace/registry.py — Plugin marketplace registry.

Stores plugin manifests in SQLite. Supports install/uninstall,
version tracking, dependency resolution, and permission declarations.

Table: marketplace_plugins
  id, name, slug, version, author, description, manifest_json,
  installed, enabled, installed_at, updated_at
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ── Schema ────────────────────────────────────────────────────────────────────

def init_marketplace_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS marketplace_plugins (
            id           TEXT PRIMARY KEY,
            slug         TEXT NOT NULL UNIQUE,
            name         TEXT NOT NULL,
            version      TEXT NOT NULL DEFAULT '1.0.0',
            author       TEXT NOT NULL DEFAULT '',
            description  TEXT NOT NULL DEFAULT '',
            manifest     TEXT NOT NULL DEFAULT '{}',
            installed    INTEGER NOT NULL DEFAULT 0,
            enabled      INTEGER NOT NULL DEFAULT 0,
            signature    TEXT,
            installed_at TEXT,
            updated_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS plugin_permissions (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            plugin_id TEXT NOT NULL REFERENCES marketplace_plugins(id) ON DELETE CASCADE,
            scope     TEXT NOT NULL,
            granted   INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS plugin_dependencies (
            plugin_id  TEXT NOT NULL REFERENCES marketplace_plugins(id) ON DELETE CASCADE,
            depends_on TEXT NOT NULL,
            version    TEXT NOT NULL DEFAULT '*',
            PRIMARY KEY (plugin_id, depends_on)
        );
    """)
    conn.commit()


# ── Manifest contract ─────────────────────────────────────────────────────────

REQUIRED_MANIFEST_FIELDS = ["id", "name", "version", "author"]

ALLOWED_PERMISSIONS = {
    "read:config",
    "write:config",
    "read:pages",
    "write:pages",
    "read:uploads",
    "write:uploads",
    "inject:head",
    "inject:body",
    "network:outbound",
}


# ── Registry ──────────────────────────────────────────────────────────────────

class PluginRegistry:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        init_marketplace_tables(conn)

    def register(self, manifest: dict, signature: str | None = None) -> str:
        """
        Register a plugin manifest. Returns plugin ID.
        Raises ValueError if manifest is invalid.
        """
        from marketplace.validator import validate_manifest
        errors = validate_manifest(manifest)
        if errors:
            raise ValueError(f"Invalid manifest: {'; '.join(errors)}")

        slug = manifest["id"]
        pid  = str(uuid.uuid4())
        now  = datetime.now(timezone.utc).isoformat()

        # Upsert by slug
        existing = self._conn.execute(
            "SELECT id FROM marketplace_plugins WHERE slug=?", (slug,)
        ).fetchone()

        if existing:
            pid = existing["id"]
            self._conn.execute("""
                UPDATE marketplace_plugins
                SET name=?, version=?, author=?, description=?, manifest=?,
                    signature=?, updated_at=?
                WHERE id=?
            """, (manifest["name"], manifest["version"], manifest.get("author",""),
                  manifest.get("description",""), json.dumps(manifest),
                  signature, now, pid))
        else:
            self._conn.execute("""
                INSERT INTO marketplace_plugins
                    (id, slug, name, version, author, description, manifest, signature, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (pid, slug, manifest["name"], manifest["version"],
                  manifest.get("author",""), manifest.get("description",""),
                  json.dumps(manifest), signature, now))

        # Register permissions
        self._conn.execute("DELETE FROM plugin_permissions WHERE plugin_id=?", (pid,))
        for scope in manifest.get("permissions", []):
            if scope in ALLOWED_PERMISSIONS:
                self._conn.execute(
                    "INSERT INTO plugin_permissions (plugin_id, scope, granted) VALUES (?,?,0)",
                    (pid, scope)
                )

        # Register dependencies
        self._conn.execute("DELETE FROM plugin_dependencies WHERE plugin_id=?", (pid,))
        for dep in manifest.get("dependencies", []):
            dep_id  = dep if isinstance(dep, str) else dep.get("id","")
            dep_ver = "*" if isinstance(dep, str) else dep.get("version","*")
            if dep_id:
                self._conn.execute(
                    "INSERT OR IGNORE INTO plugin_dependencies (plugin_id, depends_on, version) VALUES (?,?,?)",
                    (pid, dep_id, dep_ver)
                )

        self._conn.commit()
        return pid

    def get(self, slug: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM marketplace_plugins WHERE slug=?", (slug,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["manifest"] = json.loads(d["manifest"])
        d["permissions"] = self._get_permissions(d["id"])
        d["dependencies"] = self._get_dependencies(d["id"])
        return d

    def list_all(self, installed_only: bool = False) -> list[dict]:
        sql = "SELECT * FROM marketplace_plugins"
        if installed_only:
            sql += " WHERE installed=1"
        sql += " ORDER BY name"
        rows = self._conn.execute(sql).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["manifest"] = json.loads(d["manifest"])
            result.append(d)
        return result

    def install(self, slug: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        n = self._conn.execute("""
            UPDATE marketplace_plugins
            SET installed=1, installed_at=?, updated_at=?
            WHERE slug=?
        """, (now, now, slug)).rowcount
        self._conn.commit()
        return n > 0

    def uninstall(self, slug: str) -> bool:
        n = self._conn.execute("""
            UPDATE marketplace_plugins
            SET installed=0, enabled=0, updated_at=?
            WHERE slug=?
        """, (datetime.now(timezone.utc).isoformat(), slug)).rowcount
        self._conn.commit()
        return n > 0

    def grant_permission(self, slug: str, scope: str) -> None:
        row = self._conn.execute(
            "SELECT id FROM marketplace_plugins WHERE slug=?", (slug,)
        ).fetchone()
        if not row:
            raise ValueError(f"Plugin not found: {slug}")
        self._conn.execute("""
            UPDATE plugin_permissions SET granted=1
            WHERE plugin_id=? AND scope=?
        """, (row["id"], scope))
        self._conn.commit()

    def check_permission(self, slug: str, scope: str) -> bool:
        row = self._conn.execute("""
            SELECT pp.granted FROM plugin_permissions pp
            JOIN marketplace_plugins mp ON mp.id = pp.plugin_id
            WHERE mp.slug=? AND pp.scope=?
        """, (slug, scope)).fetchone()
        return bool(row and row["granted"])

    def resolve_dependencies(self, slug: str) -> list[str]:
        """Return ordered list of slugs that must be installed before slug."""
        visited: set[str] = set()
        order:   list[str] = []
        self._dfs(slug, visited, order)
        order.remove(slug)
        return order

    def _dfs(self, slug: str, visited: set, order: list) -> None:
        if slug in visited:
            return
        visited.add(slug)
        deps = self._conn.execute("""
            SELECT pd.depends_on FROM plugin_dependencies pd
            JOIN marketplace_plugins mp ON mp.id = pd.plugin_id
            WHERE mp.slug=?
        """, (slug,)).fetchall()
        for dep in deps:
            self._dfs(dep["depends_on"], visited, order)
        order.append(slug)

    def _get_permissions(self, pid: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT scope, granted FROM plugin_permissions WHERE plugin_id=?", (pid,)
        ).fetchall()
        return [dict(r) for r in rows]

    def _get_dependencies(self, pid: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT depends_on, version FROM plugin_dependencies WHERE plugin_id=?", (pid,)
        ).fetchall()
        return [dict(r) for r in rows]
