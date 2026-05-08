"""
app/routes/admin.py — Admin Panel Blueprint
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session)
from app.models.user import UserModel
import db as database

admin_bp = Blueprint("admin", __name__)


def _admin_required():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    user = UserModel.get_by_id(session["user_id"])
    if not user or not user["is_admin"]:
        flash("Admin access required.", "error")
        return redirect(url_for("dashboard.index"))
    return None


@admin_bp.route("/admin")
def index():
    r = _admin_required()
    if r: return r
    stats = database.get_platform_stats()
    users = UserModel.get_all()
    return render_template("admin/index.html", stats=stats, users=users)


@admin_bp.route("/admin/user/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    r = _admin_required()
    if r: return r
    if user_id == session["user_id"]:
        flash("Cannot delete your own account.", "error")
    else:
        UserModel.delete(user_id)
        flash("User deleted.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/admin/make-admin/<int:user_id>", methods=["POST"])
def make_admin(user_id):
    r = _admin_required()
    if r: return r
    UserModel.make_admin(user_id)
    flash("User promoted to admin.", "success")
    return redirect(url_for("admin.index"))


# ── Analytics Dashboard ───────────────────────────────────────────────────────
@admin_bp.route("/admin/analytics")
def analytics():
    r = _admin_required()
    if r: return r
    stats = database.get_platform_stats()
    return render_template("admin/analytics.html", stats=stats)


# ── Plugin Marketplace ────────────────────────────────────────────────────────
@admin_bp.route("/admin/plugins")
def plugins():
    r = _admin_required()
    if r: return r
    try:
        import sqlite3, json
        conn = sqlite3.connect(database.DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS marketplace_plugins (
                id TEXT PRIMARY KEY, slug TEXT UNIQUE, name TEXT,
                version TEXT DEFAULT '1.0.0', author TEXT DEFAULT '',
                description TEXT DEFAULT '', installed INTEGER DEFAULT 0,
                enabled INTEGER DEFAULT 0, updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        plugins_list = [dict(r) for r in conn.execute(
            "SELECT * FROM marketplace_plugins ORDER BY name"
        ).fetchall()]
        conn.close()
    except Exception:
        plugins_list = []
    return render_template("admin/plugins.html", plugins=plugins_list)


@admin_bp.route("/admin/plugins/install", methods=["POST"])
def install_plugin():
    r = _admin_required()
    if r: return r
    slug    = request.form.get("slug", "").strip()
    name    = request.form.get("name", slug).strip()
    version = request.form.get("version", "1.0.0").strip()
    author  = request.form.get("author", "").strip()
    desc    = request.form.get("description", "").strip()
    if not slug:
        flash("Plugin slug is required.", "error")
        return redirect(url_for("admin.plugins"))
    try:
        import sqlite3, uuid
        conn = sqlite3.connect(database.DB_PATH)
        conn.execute("""
            INSERT OR REPLACE INTO marketplace_plugins
                (id, slug, name, version, author, description, installed, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
        """, (str(uuid.uuid4())[:12], slug, name, version, author, desc))
        conn.commit(); conn.close()
        flash(f'Plugin "{name}" installed successfully.', "success")
    except Exception as e:
        flash(f"Install failed: {e}", "error")
    return redirect(url_for("admin.plugins"))


@admin_bp.route("/admin/plugins/uninstall/<slug>", methods=["POST"])
def uninstall_plugin(slug):
    r = _admin_required()
    if r: return r
    try:
        import sqlite3
        conn = sqlite3.connect(database.DB_PATH)
        conn.execute("UPDATE marketplace_plugins SET installed=0, enabled=0 WHERE slug=?", (slug,))
        conn.commit(); conn.close()
        flash(f'Plugin "{slug}" uninstalled.', "success")
    except Exception as e:
        flash(f"Uninstall failed: {e}", "error")
    return redirect(url_for("admin.plugins"))


# ── Notifications ─────────────────────────────────────────────────────────────
@admin_bp.route("/admin/notifications")
def notifications():
    r = _admin_required()
    if r: return r
    try:
        import sqlite3
        conn = sqlite3.connect(database.DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS admin_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL, message TEXT NOT NULL,
                type TEXT DEFAULT 'info', sent_to TEXT DEFAULT 'all',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        notifs = [dict(r) for r in conn.execute(
            "SELECT * FROM admin_notifications ORDER BY created_at DESC LIMIT 50"
        ).fetchall()]
        conn.close()
    except Exception:
        notifs = []
    return render_template("admin/notifications.html", notifications=notifs)


@admin_bp.route("/admin/notifications/send", methods=["POST"])
def send_notification():
    r = _admin_required()
    if r: return r
    title   = request.form.get("title", "").strip()
    message = request.form.get("message", "").strip()
    ntype   = request.form.get("type", "info")
    sent_to = request.form.get("sent_to", "all")
    if not title or not message:
        flash("Title and message are required.", "error")
        return redirect(url_for("admin.notifications"))
    try:
        import sqlite3
        conn = sqlite3.connect(database.DB_PATH)
        conn.execute("""
            INSERT INTO admin_notifications (title, message, type, sent_to)
            VALUES (?, ?, ?, ?)
        """, (title, message, ntype, sent_to))
        conn.commit(); conn.close()
        flash("Notification sent successfully.", "success")
    except Exception as e:
        flash(f"Failed: {e}", "error")
    return redirect(url_for("admin.notifications"))


# ── User Notifications (for logged-in users) ──────────────────────────────────
@admin_bp.route("/notifications")
def user_notifications():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    try:
        import sqlite3
        conn = sqlite3.connect(database.DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS admin_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL, message TEXT NOT NULL,
                type TEXT DEFAULT 'info', sent_to TEXT DEFAULT 'all',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        notifs = [dict(r) for r in conn.execute(
            "SELECT * FROM admin_notifications WHERE sent_to='all' ORDER BY created_at DESC LIMIT 20"
        ).fetchall()]
        conn.close()
    except Exception:
        notifs = []
    return render_template("notifications.html", notifications=notifs)
