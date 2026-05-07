"""
gateway/auth_proxy.py — Centralized auth proxy for the API gateway.

Validates session cookies and API keys.
Injects user context into g before any route handler runs.
"""
from __future__ import annotations

from flask import g, jsonify, request
from functools import wraps
from typing import Callable


def require_auth(fn: Callable) -> Callable:
    """Decorator: return 401 if user is not authenticated."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not getattr(g, "user_id", None):
            return jsonify({"success": False, "error": "Authentication required",
                            "data": {}}), 401
        return fn(*args, **kwargs)
    return wrapper


def require_scope(scope: str):
    """Decorator: require a specific API key scope."""
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if getattr(g, "auth_method", "") == "api_key":
                scopes = getattr(g, "api_key_scopes", [])
                if scope not in scopes and "admin" not in scopes:
                    return jsonify({"success": False,
                                    "error": f"API key missing scope: {scope}",
                                    "data": {}}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user() -> dict | None:
    """Return current user dict from DB, or None."""
    uid = getattr(g, "user_id", None)
    if not uid:
        return None
    try:
        from db.connection import get_conn
        from db.repositories import UserRepository
        return UserRepository(get_conn()).find_by_id(uid)
    except Exception:
        return None
