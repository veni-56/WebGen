"""
db.py — Database layer for the WebGen SaaS platform.
Schema: users, projects, project_versions, subscriptions,
        api_keys, rate_limits, prompt_cache, analytics
"""
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "platform.db")


def get_db() -> sqlite3.Connection:
    """
    Return a SQLite connection with:
    - 10-second timeout (prevents immediate lock errors)
    - WAL journal mode (allows concurrent reads + writes)
    - row_factory for dict-like access
    """
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def row_to_dict(row) -> dict:
    """Safely convert a sqlite3.Row to a plain dict. Returns {} if None."""
    if row is None:
        return {}
    try:
        return dict(row)
    except Exception:
        return {}


def init_db() -> None:
    """Create all platform tables if they don't exist (idempotent)."""
    conn = get_db()
    conn.executescript("""

        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT    UNIQUE NOT NULL,
            email        TEXT    UNIQUE NOT NULL,
            password     TEXT    NOT NULL,
            is_admin     INTEGER DEFAULT 0,
            plan         TEXT    DEFAULT 'free',
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS projects (
            id           TEXT    PRIMARY KEY,
            user_id      INTEGER NOT NULL,
            name         TEXT    NOT NULL,
            website_type TEXT    NOT NULL,
            prompt       TEXT,
            config       TEXT,
            project_type TEXT    NOT NULL,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS project_versions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT    NOT NULL,
            config     TEXT    NOT NULL,
            label      TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS subscriptions (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id            INTEGER UNIQUE NOT NULL,
            plan               TEXT    NOT NULL DEFAULT 'free',
            stripe_customer_id TEXT,
            stripe_sub_id      TEXT,
            status             TEXT    DEFAULT 'active',
            current_period_end TIMESTAMP,
            created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS api_keys (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            key_hash   TEXT    UNIQUE NOT NULL,
            key_prefix TEXT    NOT NULL,
            name       TEXT    DEFAULT 'Default',
            last_used  TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS rate_limits (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            endpoint   TEXT    NOT NULL,
            count      INTEGER DEFAULT 0,
            window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, endpoint)
        );

        CREATE TABLE IF NOT EXISTS prompt_cache (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_hash  TEXT    UNIQUE NOT NULL,
            config_json  TEXT    NOT NULL,
            result_json  TEXT    NOT NULL,
            hit_count    INTEGER DEFAULT 0,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_hit     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS analytics (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            project_id TEXT,
            event      TEXT    NOT NULL,
            meta       TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_settings (
            user_id       INTEGER PRIMARY KEY,
            default_theme TEXT DEFAULT 'modern',
            default_font  TEXT DEFAULT 'Poppins',
            preferences   TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS project_collaborators (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT    NOT NULL,
            user_id    INTEGER NOT NULL,
            role       TEXT    DEFAULT 'viewer',
            added_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(project_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS marketplace_templates (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id   INTEGER NOT NULL,
            name        TEXT    NOT NULL,
            description TEXT,
            price       REAL    DEFAULT 0,
            config      TEXT    NOT NULL,
            preview_img TEXT,
            downloads   INTEGER DEFAULT 0,
            rating      REAL    DEFAULT 0,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS chat_sessions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            session_id TEXT    UNIQUE NOT NULL,
            state      TEXT    DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS plugins (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id  TEXT    NOT NULL,
            plugin_type TEXT    NOT NULL,
            config      TEXT    DEFAULT '{}',
            enabled     INTEGER DEFAULT 1,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
    """)
    conn.commit()

    # ── Schema migrations (add missing columns to existing databases) ─────
    _migrate(conn)
    conn.close()


def _migrate(conn: sqlite3.Connection) -> None:
    """
    Safely add columns that may be missing from older database versions.
    ALTER TABLE ADD COLUMN is idempotent — we catch errors if column exists.
    """
    migrations = [
        # users table additions
        ("ALTER TABLE users ADD COLUMN plan TEXT DEFAULT 'free'",),
        ("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0",),
        # user_settings additions
        ("ALTER TABLE user_settings ADD COLUMN preferences TEXT DEFAULT '{}'",),
        # projects additions — use NULL default (CURRENT_TIMESTAMP not allowed in ALTER TABLE)
        ("ALTER TABLE projects ADD COLUMN updated_at TIMESTAMP",),
    ]
    for (sql,) in migrations:
        try:
            conn.execute(sql)
        except Exception:
            pass  # Column already exists — safe to ignore
    conn.commit()


# ── User helpers ──────────────────────────────────────────────────────────────

def create_user(username: str, email: str, password_hash: str) -> bool:
    """Insert a new user. Returns False if username/email already exists."""
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?,?,?)",
            (username, email, password_hash)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def get_user_by_username(username: str):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return user


def get_user_by_id(user_id: int):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return user


def update_user_password(user_id: int, new_hash: str) -> None:
    conn = get_db()
    conn.execute("UPDATE users SET password=? WHERE id=?", (new_hash, user_id))
    conn.commit()
    conn.close()


def get_all_users() -> list:
    """Admin: get all users with project counts."""
    conn = get_db()
    rows = conn.execute("""
        SELECT u.*, COUNT(p.id) as project_count
        FROM users u
        LEFT JOIN projects p ON p.user_id = u.id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """).fetchall()
    conn.close()
    return rows


def delete_user(user_id: int) -> None:
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


# ── Project helpers ───────────────────────────────────────────────────────────

def save_project(project_id: str, user_id: int, name: str,
                 website_type: str, prompt: str, config: str,
                 project_type: str) -> None:
    conn = get_db()
    # Check if updated_at column exists
    cols = [r[1] for r in conn.execute("PRAGMA table_info(projects)").fetchall()]
    if "updated_at" in cols:
        conn.execute(
            """INSERT OR REPLACE INTO projects
               (id, user_id, name, website_type, prompt, config, project_type, updated_at)
               VALUES (?,?,?,?,?,?,?, CURRENT_TIMESTAMP)""",
            (project_id, user_id, name, website_type, prompt, config, project_type)
        )
    else:
        conn.execute(
            """INSERT OR REPLACE INTO projects
               (id, user_id, name, website_type, prompt, config, project_type)
               VALUES (?,?,?,?,?,?,?)""",
            (project_id, user_id, name, website_type, prompt, config, project_type)
        )
    conn.commit()
    conn.close()


def update_project_config(project_id: str, user_id: int,
                          name: str, config: str) -> bool:
    """Update project name and config. Returns False if not found/owned."""
    conn = get_db()
    cols = [r[1] for r in conn.execute("PRAGMA table_info(projects)").fetchall()]
    if "updated_at" in cols:
        cur = conn.execute(
            """UPDATE projects SET name=?, config=?, updated_at=CURRENT_TIMESTAMP
               WHERE id=? AND user_id=?""",
            (name, config, project_id, user_id)
        )
    else:
        cur = conn.execute(
            "UPDATE projects SET name=?, config=? WHERE id=? AND user_id=?",
            (name, config, project_id, user_id)
        )
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed


def get_user_projects(user_id: int) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM projects WHERE user_id=? ORDER BY COALESCE(updated_at, created_at) DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return rows


def get_project(project_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    conn.close()
    return row


def delete_project(project_id: str, user_id: int) -> None:
    conn = get_db()
    conn.execute("DELETE FROM projects WHERE id=? AND user_id=?", (project_id, user_id))
    conn.commit()
    conn.close()


def duplicate_project(project_id: str, user_id: int, new_id: str) -> bool:
    """Clone a project under a new ID."""
    conn = get_db()
    src = conn.execute(
        "SELECT * FROM projects WHERE id=? AND user_id=?", (project_id, user_id)
    ).fetchone()
    if not src:
        conn.close()
        return False
    conn.execute(
        """INSERT INTO projects (id, user_id, name, website_type, prompt, config, project_type)
           VALUES (?,?,?,?,?,?,?)""",
        (new_id, user_id, src["name"] + " (copy)", src["website_type"],
         src["prompt"], src["config"], src["project_type"])
    )
    conn.commit()
    conn.close()
    return True


def rename_project(project_id: str, user_id: int, new_name: str) -> bool:
    conn = get_db()
    cols = [r[1] for r in conn.execute("PRAGMA table_info(projects)").fetchall()]
    if "updated_at" in cols:
        cur = conn.execute(
            "UPDATE projects SET name=?, updated_at=CURRENT_TIMESTAMP WHERE id=? AND user_id=?",
            (new_name, project_id, user_id)
        )
    else:
        cur = conn.execute(
            "UPDATE projects SET name=? WHERE id=? AND user_id=?",
            (new_name, project_id, user_id)
        )
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed


# ── Version history ───────────────────────────────────────────────────────────

def save_version(project_id: str, config: str, label: str = "") -> None:
    conn = get_db()
    conn.execute(
        "INSERT INTO project_versions (project_id, config, label) VALUES (?,?,?)",
        (project_id, config, label)
    )
    conn.commit()
    conn.close()


def get_versions(project_id: str) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM project_versions WHERE project_id=? ORDER BY created_at DESC LIMIT 10",
        (project_id,)
    ).fetchall()
    conn.close()
    return rows


# ── Analytics ─────────────────────────────────────────────────────────────────

def log_event(user_id: int, project_id: str, event: str, meta: dict = None) -> None:
    conn = get_db()
    conn.execute(
        "INSERT INTO analytics (user_id, project_id, event, meta) VALUES (?,?,?,?)",
        (user_id, project_id, event, json.dumps(meta or {}))
    )
    conn.commit()
    conn.close()


def get_platform_stats() -> dict:
    """Admin: aggregate platform statistics."""
    conn = get_db()
    stats = {
        "total_users":    conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "total_projects": conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0],
        "by_type":        {r["project_type"]: r["cnt"] for r in conn.execute(
            "SELECT project_type, COUNT(*) as cnt FROM projects GROUP BY project_type"
        ).fetchall()},
        "recent_users":   conn.execute(
            "SELECT username, email, created_at FROM users ORDER BY created_at DESC LIMIT 5"
        ).fetchall(),
        "recent_projects": conn.execute(
            """SELECT p.name, p.project_type, u.username, p.created_at
               FROM projects p JOIN users u ON p.user_id=u.id
               ORDER BY p.created_at DESC LIMIT 5"""
        ).fetchall(),
    }
    conn.close()
    return stats


# ── Subscription helpers ──────────────────────────────────────────────────────

def get_subscription(user_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM subscriptions WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return row


def upsert_subscription(user_id: int, plan: str, stripe_customer_id: str = None,
                         stripe_sub_id: str = None, status: str = "active",
                         period_end: str = None) -> None:
    conn = get_db()
    conn.execute("""
        INSERT INTO subscriptions (user_id, plan, stripe_customer_id, stripe_sub_id, status, current_period_end)
        VALUES (?,?,?,?,?,?)
        ON CONFLICT(user_id) DO UPDATE SET
            plan=excluded.plan,
            stripe_customer_id=COALESCE(excluded.stripe_customer_id, stripe_customer_id),
            stripe_sub_id=COALESCE(excluded.stripe_sub_id, stripe_sub_id),
            status=excluded.status,
            current_period_end=excluded.current_period_end,
            updated_at=CURRENT_TIMESTAMP
    """, (user_id, plan, stripe_customer_id, stripe_sub_id, status, period_end))
    # Also update users.plan
    conn.execute("UPDATE users SET plan=? WHERE id=?", (plan, user_id))
    conn.commit()
    conn.close()


def get_user_plan(user_id: int) -> str:
    conn = get_db()
    row = conn.execute("SELECT plan FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    if not row:
        return "free"
    try:
        return row["plan"] or "free"
    except (IndexError, KeyError):
        return "free"


# ── API key helpers ───────────────────────────────────────────────────────────

def create_api_key(user_id: int, key_hash: str, key_prefix: str, name: str = "Default") -> None:
    conn = get_db()
    conn.execute(
        "INSERT INTO api_keys (user_id, key_hash, key_prefix, name) VALUES (?,?,?,?)",
        (user_id, key_hash, key_prefix, name)
    )
    conn.commit()
    conn.close()


def get_api_key(key_hash: str):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM api_keys WHERE key_hash=?", (key_hash,)
    ).fetchone()
    if row:
        conn.execute("UPDATE api_keys SET last_used=CURRENT_TIMESTAMP WHERE key_hash=?", (key_hash,))
        conn.commit()
    conn.close()
    return row


def get_user_api_keys(user_id: int) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT id, key_prefix, name, last_used, created_at FROM api_keys WHERE user_id=? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return rows


def delete_api_key(key_id: int, user_id: int) -> None:
    conn = get_db()
    conn.execute("DELETE FROM api_keys WHERE id=? AND user_id=?", (key_id, user_id))
    conn.commit()
    conn.close()


# ── Rate limit helpers ────────────────────────────────────────────────────────

def get_rate_limit(user_id: int, endpoint: str) -> dict:
    """Get current rate limit count for a user+endpoint in the current hour window."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM rate_limits WHERE user_id=? AND endpoint=?",
        (user_id, endpoint)
    ).fetchone()
    conn.close()
    return row_to_dict(row) if row else {"count": 0, "window_start": None}


def increment_rate_limit(user_id: int, endpoint: str) -> int:
    """Increment counter, reset if window expired (1 hour). Returns new count."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM rate_limits WHERE user_id=? AND endpoint=?",
        (user_id, endpoint)
    ).fetchone()

    from datetime import datetime, timedelta
    now = datetime.utcnow()

    if row:
        window_start = datetime.fromisoformat(row["window_start"]) if row["window_start"] else now
        if now - window_start > timedelta(hours=1):
            # Reset window
            conn.execute(
                "UPDATE rate_limits SET count=1, window_start=? WHERE user_id=? AND endpoint=?",
                (now.isoformat(), user_id, endpoint)
            )
            new_count = 1
        else:
            conn.execute(
                "UPDATE rate_limits SET count=count+1 WHERE user_id=? AND endpoint=?",
                (user_id, endpoint)
            )
            new_count = row["count"] + 1
    else:
        conn.execute(
            "INSERT INTO rate_limits (user_id, endpoint, count, window_start) VALUES (?,?,1,?)",
            (user_id, endpoint, now.isoformat())
        )
        new_count = 1

    conn.commit()
    conn.close()
    return new_count


# ── Prompt cache helpers ──────────────────────────────────────────────────────

def get_cached_prompt(prompt_hash: str):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM prompt_cache WHERE prompt_hash=?", (prompt_hash,)
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE prompt_cache SET hit_count=hit_count+1, last_hit=CURRENT_TIMESTAMP WHERE prompt_hash=?",
            (prompt_hash,)
        )
        conn.commit()
    conn.close()
    return row


def save_prompt_cache(prompt_hash: str, config_json: str, result_json: str) -> None:
    conn = get_db()
    conn.execute("""
        INSERT OR REPLACE INTO prompt_cache (prompt_hash, config_json, result_json)
        VALUES (?,?,?)
    """, (prompt_hash, config_json, result_json))
    conn.commit()
    conn.close()


def get_cache_stats() -> dict:
    conn = get_db()
    stats = {
        "total_cached":  conn.execute("SELECT COUNT(*) FROM prompt_cache").fetchone()[0],
        "total_hits":    conn.execute("SELECT COALESCE(SUM(hit_count),0) FROM prompt_cache").fetchone()[0],
        "top_cached":    conn.execute(
            "SELECT prompt_hash, hit_count, created_at FROM prompt_cache ORDER BY hit_count DESC LIMIT 5"
        ).fetchall(),
    }
    conn.close()
    return stats


# ── Enhanced analytics ────────────────────────────────────────────────────────

def get_full_analytics() -> dict:
    """Admin: full platform analytics for the analytics dashboard."""
    conn = get_db()

    # Daily signups (last 30 days)
    daily_signups = conn.execute("""
        SELECT DATE(created_at) as day, COUNT(*) as count
        FROM users
        WHERE created_at >= DATE('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY day
    """).fetchall()

    # Daily generations (last 30 days)
    daily_gens = conn.execute("""
        SELECT DATE(created_at) as day, COUNT(*) as count
        FROM analytics
        WHERE event IN ('generate','codegen','prompt_generate','api_codegen')
          AND created_at >= DATE('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY day
    """).fetchall()

    # Plan distribution
    plan_dist = conn.execute("""
        SELECT COALESCE(plan,'free') as plan, COUNT(*) as count FROM users GROUP BY COALESCE(plan,'free')
    """).fetchall()

    # Top generators
    top_types = conn.execute("""
        SELECT project_type, COUNT(*) as count
        FROM projects GROUP BY project_type ORDER BY count DESC
    """).fetchall()

    # Active users (generated in last 7 days)
    active_users = conn.execute("""
        SELECT COUNT(DISTINCT user_id) FROM analytics
        WHERE created_at >= DATE('now', '-7 days')
    """).fetchone()[0]

    # Total generations
    total_gens = conn.execute("""
        SELECT COUNT(*) FROM analytics
        WHERE event IN ('generate','codegen','prompt_generate','api_codegen')
    """).fetchone()[0]

    # Revenue estimate (pro=9.99/mo, business=29.99/mo)
    plan_counts = {r["plan"]: r["count"] for r in plan_dist}
    revenue_est = (plan_counts.get("pro", 0) * 9.99 +
                   plan_counts.get("business", 0) * 29.99)

    conn.close()
    return {
        "daily_signups":  [dict(r) for r in daily_signups],
        "daily_gens":     [dict(r) for r in daily_gens],
        "plan_dist":      {r["plan"]: r["count"] for r in plan_dist},
        "top_types":      [dict(r) for r in top_types],
        "active_users":   active_users,
        "total_gens":     total_gens,
        "revenue_est":    round(revenue_est, 2),
    }


def update_user_plan(user_id, plan: str) -> None:
    """Update a user's subscription plan."""
    conn = get_db()
    conn.execute("UPDATE users SET plan=? WHERE id=?", (plan, user_id))
    conn.commit()
    conn.close()
