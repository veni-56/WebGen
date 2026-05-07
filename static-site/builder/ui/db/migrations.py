"""
Migration runner for the Website Builder SaaS platform.

Migrations are applied in version order.  Applied versions are tracked in the
``schema_migrations`` table so each migration runs exactly once.

Usage::

    from db.connection import get_conn
    from db.migrations import run_migrations

    conn = get_conn()
    run_migrations(conn)
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import TypedDict


# ---------------------------------------------------------------------------
# Migration type
# ---------------------------------------------------------------------------

class Migration(TypedDict):
    version: int
    name: str
    sql: str


# ---------------------------------------------------------------------------
# Migration definitions
# ---------------------------------------------------------------------------

MIGRATIONS: list[Migration] = [
    # ------------------------------------------------------------------
    # 1. Users
    # ------------------------------------------------------------------
    {
        "version": 1,
        "name": "create_users",
        "sql": """
            CREATE TABLE IF NOT EXISTS users (
                id            TEXT PRIMARY KEY,
                email         TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """,
    },
    # ------------------------------------------------------------------
    # 2. Organizations
    # ------------------------------------------------------------------
    {
        "version": 2,
        "name": "create_organizations",
        "sql": """
            CREATE TABLE IF NOT EXISTS organizations (
                id         TEXT PRIMARY KEY,
                name       TEXT NOT NULL,
                slug       TEXT NOT NULL UNIQUE,
                plan       TEXT NOT NULL DEFAULT 'free',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """,
    },
    # ------------------------------------------------------------------
    # 3. Workspaces
    # ------------------------------------------------------------------
    {
        "version": 3,
        "name": "create_workspaces",
        "sql": """
            CREATE TABLE IF NOT EXISTS workspaces (
                id         TEXT PRIMARY KEY,
                org_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                name       TEXT NOT NULL,
                slug       TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(org_id, slug)
            );
        """,
    },
    # ------------------------------------------------------------------
    # 4. Org members
    # ------------------------------------------------------------------
    {
        "version": 4,
        "name": "create_org_members",
        "sql": """
            CREATE TABLE IF NOT EXISTS org_members (
                id         TEXT PRIMARY KEY,
                org_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role       TEXT NOT NULL CHECK(role IN ('owner', 'admin', 'editor', 'viewer')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(org_id, user_id)
            );
        """,
    },
    # ------------------------------------------------------------------
    # 5. Projects
    # ------------------------------------------------------------------
    {
        "version": 5,
        "name": "create_projects",
        "sql": """
            CREATE TABLE IF NOT EXISTS projects (
                id           TEXT PRIMARY KEY,
                org_id       TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                workspace_id TEXT REFERENCES workspaces(id) ON DELETE SET NULL,
                user_id      TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name         TEXT NOT NULL,
                slug         TEXT NOT NULL UNIQUE,
                config       TEXT NOT NULL DEFAULT '{}',
                config_hash  TEXT NOT NULL DEFAULT '',
                published    INTEGER NOT NULL DEFAULT 0,
                publish_url  TEXT NOT NULL DEFAULT '',
                created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """,
    },
    # ------------------------------------------------------------------
    # 6. Publish versions, project uploads, CSRF tokens, jobs
    # ------------------------------------------------------------------
    {
        "version": 6,
        "name": "create_publish_versions_uploads_csrf_jobs",
        "sql": """
            CREATE TABLE IF NOT EXISTS publish_versions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                version    TEXT NOT NULL,
                url        TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS project_uploads (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                filename   TEXT NOT NULL,
                url        TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS csrf_tokens (
                token      TEXT PRIMARY KEY,
                user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS jobs (
                id         TEXT PRIMARY KEY,
                type       TEXT NOT NULL,
                status     TEXT NOT NULL DEFAULT 'pending'
                               CHECK(status IN ('pending', 'running', 'done', 'failed')),
                payload    TEXT NOT NULL DEFAULT '{}',
                result     TEXT,
                error      TEXT,
                user_id    TEXT REFERENCES users(id) ON DELETE SET NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """,
    },
    # ------------------------------------------------------------------
    # 7. API keys
    # ------------------------------------------------------------------
    {
        "version": 7,
        "name": "create_api_keys",
        "sql": """
            CREATE TABLE IF NOT EXISTS api_keys (
                id         TEXT PRIMARY KEY,
                user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                org_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                key_hash   TEXT NOT NULL UNIQUE,
                name       TEXT NOT NULL,
                scopes     TEXT NOT NULL DEFAULT '[]',
                last_used  TEXT,
                expires_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """,
    },
    # ------------------------------------------------------------------
    # 8. Audit logs
    # ------------------------------------------------------------------
    {
        "version": 8,
        "name": "create_audit_logs",
        "sql": """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                org_id        TEXT REFERENCES organizations(id) ON DELETE SET NULL,
                user_id       TEXT REFERENCES users(id) ON DELETE SET NULL,
                action        TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id   TEXT NOT NULL,
                metadata      TEXT,
                ip            TEXT,
                created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_audit_logs_org_id
                ON audit_logs(org_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_audit_logs_resource
                ON audit_logs(resource_type, resource_id);
        """,
    },
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def _ensure_migrations_table(conn: sqlite3.Connection) -> None:
    """Create the schema_migrations tracking table if it does not exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version    INTEGER PRIMARY KEY,
            name       TEXT    NOT NULL,
            applied_at TEXT    NOT NULL
        )
        """
    )
    conn.commit()


def _applied_versions(conn: sqlite3.Connection) -> set[int]:
    """Return the set of already-applied migration versions."""
    rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
    return {row[0] for row in rows}


def run_migrations(conn: sqlite3.Connection) -> None:
    """
    Apply all pending migrations in ascending version order.

    Each migration is executed inside its own transaction so a failure in
    migration N does not affect already-applied migrations 1…N-1.
    """
    _ensure_migrations_table(conn)
    applied = _applied_versions(conn)

    pending = sorted(
        (m for m in MIGRATIONS if m["version"] not in applied),
        key=lambda m: m["version"],
    )

    for migration in pending:
        try:
            conn.executescript(migration["sql"])
            conn.execute(
                "INSERT INTO schema_migrations (version, name, applied_at) VALUES (?, ?, ?)",
                (
                    migration["version"],
                    migration["name"],
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
        except sqlite3.Error as exc:
            conn.rollback()
            raise RuntimeError(
                f"Migration {migration['version']} ({migration['name']}) failed: {exc}"
            ) from exc
