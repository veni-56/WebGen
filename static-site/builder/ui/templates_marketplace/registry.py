"""
templates_marketplace/registry.py — Template marketplace registry.

Stores published templates with versioning, ratings, categories,
and usage analytics.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone


def init_template_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS template_registry (
            id           TEXT PRIMARY KEY,
            slug         TEXT NOT NULL UNIQUE,
            name         TEXT NOT NULL,
            description  TEXT NOT NULL DEFAULT '',
            author_id    TEXT NOT NULL,
            category     TEXT NOT NULL DEFAULT 'general',
            tags         TEXT NOT NULL DEFAULT '[]',
            version      TEXT NOT NULL DEFAULT '1.0.0',
            preview_url  TEXT NOT NULL DEFAULT '',
            template_json TEXT NOT NULL DEFAULT '{}',
            published    INTEGER NOT NULL DEFAULT 0,
            downloads    INTEGER NOT NULL DEFAULT 0,
            created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS template_ratings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id TEXT NOT NULL REFERENCES template_registry(id) ON DELETE CASCADE,
            user_id     TEXT NOT NULL,
            rating      INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            review      TEXT,
            created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(template_id, user_id)
        );
        CREATE TABLE IF NOT EXISTS template_versions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id TEXT NOT NULL REFERENCES template_registry(id) ON DELETE CASCADE,
            version     TEXT NOT NULL,
            template_json TEXT NOT NULL,
            changelog   TEXT NOT NULL DEFAULT '',
            created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_template_category
            ON template_registry(category, published);
        CREATE INDEX IF NOT EXISTS idx_template_downloads
            ON template_registry(downloads DESC);
    """)
    conn.commit()


class TemplateRegistry:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        init_template_tables(conn)

    def publish(self, author_id: str, name: str, slug: str,
                template: dict, category: str = "general",
                description: str = "", tags: list | None = None,
                preview_url: str = "") -> str:
        """Publish a new template. Returns template ID."""
        tid  = str(uuid.uuid4())
        now  = datetime.now(timezone.utc).isoformat()
        tags = tags or []
        self._conn.execute("""
            INSERT INTO template_registry
                (id, slug, name, description, author_id, category, tags,
                 template_json, preview_url, published, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,1,?,?)
        """, (tid, slug, name, description, author_id, category,
              json.dumps(tags), json.dumps(template), preview_url, now, now))
        # Record initial version
        self._conn.execute("""
            INSERT INTO template_versions (template_id, version, template_json)
            VALUES (?,?,?)
        """, (tid, "1.0.0", json.dumps(template)))
        self._conn.commit()
        return tid

    def update_version(self, template_id: str, template: dict,
                       version: str, changelog: str = "") -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute("""
            UPDATE template_registry
            SET template_json=?, version=?, updated_at=?
            WHERE id=?
        """, (json.dumps(template), version, now, template_id))
        self._conn.execute("""
            INSERT INTO template_versions (template_id, version, template_json, changelog)
            VALUES (?,?,?,?)
        """, (template_id, version, json.dumps(template), changelog))
        self._conn.commit()

    def get(self, slug: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM template_registry WHERE slug=? AND published=1", (slug,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["template"] = json.loads(d["template_json"])
        d["tags"]     = json.loads(d["tags"])
        d["rating"]   = self._avg_rating(d["id"])
        return d

    def search(self, query: str = "", category: str = "",
               limit: int = 20, offset: int = 0) -> list[dict]:
        sql    = "SELECT * FROM template_registry WHERE published=1"
        params: list = []
        if query:
            sql += " AND (name LIKE ? OR description LIKE ?)"
            params += [f"%{query}%", f"%{query}%"]
        if category:
            sql += " AND category=?"
            params.append(category)
        sql += " ORDER BY downloads DESC LIMIT ? OFFSET ?"
        params += [limit, offset]
        rows = self._conn.execute(sql, params).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["tags"]   = json.loads(d["tags"])
            d["rating"] = self._avg_rating(d["id"])
            d.pop("template_json", None)
            result.append(d)
        return result

    def categories(self) -> list[dict]:
        rows = self._conn.execute("""
            SELECT category, COUNT(*) as count
            FROM template_registry WHERE published=1
            GROUP BY category ORDER BY count DESC
        """).fetchall()
        return [dict(r) for r in rows]

    def rate(self, template_id: str, user_id: str,
             rating: int, review: str = "") -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute("""
            INSERT INTO template_ratings (template_id, user_id, rating, review, created_at)
            VALUES (?,?,?,?,?)
            ON CONFLICT(template_id, user_id) DO UPDATE
            SET rating=excluded.rating, review=excluded.review
        """, (template_id, user_id, rating, review, now))
        self._conn.commit()

    def record_install(self, template_id: str) -> None:
        self._conn.execute(
            "UPDATE template_registry SET downloads=downloads+1 WHERE id=?",
            (template_id,)
        )
        self._conn.commit()

    def get_versions(self, template_id: str) -> list[dict]:
        rows = self._conn.execute("""
            SELECT version, changelog, created_at
            FROM template_versions WHERE template_id=?
            ORDER BY created_at DESC
        """, (template_id,)).fetchall()
        return [dict(r) for r in rows]

    def _avg_rating(self, template_id: str) -> dict:
        row = self._conn.execute("""
            SELECT AVG(rating) as avg, COUNT(*) as count
            FROM template_ratings WHERE template_id=?
        """, (template_id,)).fetchone()
        return {
            "avg":   round(row["avg"] or 0, 1),
            "count": row["count"] or 0,
        }
