"""
gateway/middleware.py — API gateway middleware stack.

Provides a composable middleware chain for Flask.
Each middleware wraps the request/response cycle.

Middleware included:
  - RequestIDMiddleware   — attach X-Request-ID
  - TracingMiddleware     — start/end trace span
  - TenantMiddleware      — resolve org + workspace
  - AuthMiddleware        — session + API key auth
  - ErrorMiddleware       — unified error formatting
"""
from __future__ import annotations

import time
import uuid
from functools import wraps
from typing import Callable

from flask import g, jsonify, request


# ── Request ID ────────────────────────────────────────────────────────────────

def attach_request_id():
    """Attach a unique request ID to every request."""
    g.request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    g.request_start = time.monotonic()


def stamp_request_id(response):
    """Echo request ID and timing in response headers."""
    response.headers["X-Request-ID"] = getattr(g, "request_id", "")
    if hasattr(g, "request_start"):
        ms = round((time.monotonic() - g.request_start) * 1000)
        response.headers["X-Response-Time"] = f"{ms}ms"
    return response


# ── Tenant resolution ─────────────────────────────────────────────────────────

def resolve_tenant():
    """
    Resolve org_id and workspace_id from headers or query params.
    Sets g.org_id, g.workspace_id, g.member_role.
    """
    g.org_id       = (request.headers.get("X-Org-ID")
                      or request.args.get("org_id", ""))
    g.workspace_id = (request.headers.get("X-Workspace-ID")
                      or request.args.get("workspace_id", ""))
    g.member_role  = None

    if getattr(g, "user_id", None) and g.org_id:
        try:
            from db.connection import get_conn
            from db.repositories import OrgRepository
            conn   = get_conn()
            member = OrgRepository(conn).get_member(g.org_id, g.user_id)
            if member:
                g.member_role = member["role"]
        except Exception:
            pass


# ── Auth resolution ───────────────────────────────────────────────────────────

def resolve_auth():
    """
    Resolve user from session or API key.
    Sets g.user_id, g.auth_method.
    """
    from flask import session as flask_session
    g.user_id    = flask_session.get("user_id")
    g.auth_method = "session"

    if not g.user_id:
        api_key = (request.headers.get("X-API-Key")
                   or request.headers.get("Authorization", "").removeprefix("Bearer "))
        if api_key and api_key.startswith("wbs_"):
            try:
                from db.connection import get_conn
                from security.api_keys import verify_api_key
                conn = get_conn()
                key_data = verify_api_key(conn, api_key)
                if key_data:
                    g.user_id    = key_data["user_id"]
                    g.auth_method = "api_key"
                    g.api_key_scopes = key_data.get("scopes", [])
            except Exception:
                pass


# ── Unified error handler ─────────────────────────────────────────────────────

def make_error_handler(app):
    """Register unified JSON error handlers on a Flask app."""

    @app.errorhandler(400)
    def bad_request(e):
        return _err(str(e), 400)

    @app.errorhandler(401)
    def unauthorized(e):
        return _err("Authentication required", 401)

    @app.errorhandler(403)
    def forbidden(e):
        return _err("Access denied", 403)

    @app.errorhandler(404)
    def not_found(e):
        return _err("Not found", 404)

    @app.errorhandler(429)
    def too_many(e):
        return _err("Rate limit exceeded", 429)

    @app.errorhandler(500)
    def server_error(e):
        return _err("Internal server error", 500)

    @app.errorhandler(Exception)
    def catch_all(e):
        import traceback
        try:
            from logger_server import slog
            slog("UNHANDLED_ERROR", {"error": str(e), "tb": traceback.format_exc()[-500:]}, "ERROR")
        except Exception:
            pass
        return _err("Internal server error", 500)


def _err(msg: str, status: int):
    rid = getattr(g, "request_id", "")
    return jsonify({
        "success": False, "error": msg, "data": {},
        "request_id": rid, "status": status,
    }), status


# ── Register all middleware on a Flask app ────────────────────────────────────

def register_middleware(app) -> None:
    """Attach all gateway middleware to a Flask app."""
    app.before_request(attach_request_id)
    app.before_request(resolve_auth)
    app.before_request(resolve_tenant)
    app.after_request(stamp_request_id)
    make_error_handler(app)
