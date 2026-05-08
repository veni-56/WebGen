"""
app/routes/auth.py — Authentication Blueprint
Handles: signup, login, logout, account settings
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session)
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import UserModel

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = UserModel.get_by_username(username)
        if user and check_password_hash(user["password"], password):
            session["user_id"]  = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = bool(user["is_admin"])
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("dashboard.index"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        username = request.form["username"].strip()
        email    = request.form["email"].strip()
        pwd      = request.form["password"]
        if len(pwd) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("signup.html")
        if UserModel.create(username, email, generate_password_hash(pwd)):
            flash("Account created! Please login.", "success")
            return redirect(url_for("auth.login"))
        flash("Username or email already exists.", "error")
    return render_template("signup.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@auth_bp.route("/account", methods=["GET", "POST"])
def account():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        current = request.form.get("current_password", "")
        new_pwd = request.form.get("new_password", "")
        user = UserModel.get_by_id(session["user_id"])
        if not check_password_hash(user["password"], current):
            flash("Current password is incorrect.", "error")
        elif len(new_pwd) < 6:
            flash("New password must be at least 6 characters.", "error")
        else:
            UserModel.update_password(session["user_id"], generate_password_hash(new_pwd))
            flash("Password updated successfully.", "success")
    user     = UserModel.get_by_id(session["user_id"])
    from app.models.project import ProjectModel
    projects = ProjectModel.get_for_user(session["user_id"])
    return render_template("account.html", user=user, project_count=len(projects))


# ── API Keys Management ───────────────────────────────────────────────────────
import secrets as _secrets
import sqlite3 as _sqlite3
import db as _database

@auth_bp.route("/api-keys")
def api_keys():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    conn = _sqlite3.connect(_database.DB_PATH)
    conn.row_factory = _sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            key_prefix TEXT NOT NULL,
            key_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_used TEXT
        )
    """)
    conn.commit()
    keys = [dict(r) for r in conn.execute(
        "SELECT id, name, key_prefix, created_at, last_used FROM api_keys WHERE user_id=? ORDER BY created_at DESC",
        (session["user_id"],)
    ).fetchall()]
    conn.close()
    return render_template("api_keys.html", api_keys=keys)


@auth_bp.route("/api-keys/create", methods=["POST"])
def create_api_key():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    name = request.form.get("name", "My API Key").strip()
    raw_key = "wbg_" + _secrets.token_hex(24)
    prefix  = raw_key[:12] + "..."
    from werkzeug.security import generate_password_hash
    key_hash = generate_password_hash(raw_key)
    conn = _sqlite3.connect(_database.DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, name TEXT NOT NULL,
            key_prefix TEXT NOT NULL, key_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP, last_used TEXT
        )
    """)
    conn.execute(
        "INSERT INTO api_keys (user_id, name, key_prefix, key_hash) VALUES (?,?,?,?)",
        (session["user_id"], name, prefix, key_hash)
    )
    conn.commit(); conn.close()
    flash(f'API Key created: {raw_key} — Copy it now, it won\'t be shown again!', "success")
    return redirect(url_for("auth.api_keys"))


@auth_bp.route("/api-keys/delete/<int:key_id>", methods=["POST"])
def delete_api_key(key_id):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    conn = _sqlite3.connect(_database.DB_PATH)
    conn.execute("DELETE FROM api_keys WHERE id=? AND user_id=?", (key_id, session["user_id"]))
    conn.commit(); conn.close()
    flash("API key deleted.", "success")
    return redirect(url_for("auth.api_keys"))


# ── Collaboration Sessions ────────────────────────────────────────────────────
@auth_bp.route("/collab/<project_id>")
def collab(project_id):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    from app.models.project import ProjectModel
    project = ProjectModel.get_by_id(project_id)
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for("dashboard.index"))
    # Get active collaborators (mock for now)
    collaborators = [{"username": session["username"], "status": "online", "cursor": "home"}]
    return render_template("collab.html", project=project, collaborators=collaborators)
