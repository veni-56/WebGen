"""
security/rbac.py — Role-Based Access Control middleware.

Role hierarchy (lowest → highest):
    viewer < editor < admin < owner

Usage (Flask decorator):
    @require_role('editor')
    def my_route(): ...

    @require_permission('projects', 'write')
    def create_project(): ...
"""
from __future__ import annotations

import functools
from flask import g, request
from typing import Callable

ROLE_WEIGHTS = {"viewer": 1, "editor": 2, "admin": 3, "owner": 4}

# Permission matrix: resource → action → minimum role
PERMISSIONS: dict[str, dict[str, str]] = {
    "projects":   {"read": "viewer", "write": "editor", "delete": "admin",  "publish": "editor"},
    "workspaces": {"read": "viewer", "write": "admin",  "delete": "owner"},
    "members":    {"read": "viewer", "write": "admin",  "delete": "owner"},
    "settings":   {"read": "admin",  "write": "admin",  "delete": "owner"},
    "billing":    {"read": "owner",  "write": "owner",  "delete": "owner"},
    "api_keys":   {"read": "admin",  "write": "admin",  "delete": "admin"},
    "audit_logs": {"read": "admin"},
}


def has_role(user_role: str, required_role: str) -> bool:
    return ROLE_WEIGHTS.get(user_role, 0) >= ROLE_WEIGHTS.get(required_role, 99)


def can(user_role: str, resource: str, action: str) -> bool:
    min_role = PERMISSIONS.get(resource, {}).get(action)
    if min_role is None:
        return False
    return has_role(user_role, min_role)


def require_role(min_role: str):
    """Decorator: require the current user to have at least min_role in the org."""
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            from flask import jsonify
            role = getattr(g, "member_role", None)
            if not role or not has_role(role, min_role):
                return jsonify({"success": False, "error": "Insufficient permissions",
                                "required": min_role, "actual": role}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_permission(resource: str, action: str):
    """Decorator: require the current user to have permission for resource+action."""
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            from flask import jsonify
            role = getattr(g, "member_role", None)
            if not role or not can(role, resource, action):
                return jsonify({"success": False,
                                "error": f"Permission denied: {resource}:{action}"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
