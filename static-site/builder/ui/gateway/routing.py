"""
gateway/routing.py — API version routing and blueprint registration.

Registers all versioned API blueprints on the Flask app.
Provides backward-compatible routing: /api/ → legacy, /api/v1/ → v1.
"""
from __future__ import annotations

from flask import Flask


def register_all_routes(app: Flask) -> None:
    """Register all API blueprints. Safe to call multiple times (idempotent)."""
    registered = {bp.name for bp in app.blueprints.values()}

    # v1 blueprint
    if "api_v1" not in registered:
        try:
            from api.v1.routes import v1
            app.register_blueprint(v1)
        except Exception as e:
            print(f"[Gateway] v1 blueprint failed: {e}")

    # Future: v2 blueprint
    # if "api_v2" not in registered:
    #     from api.v2.routes import v2
    #     app.register_blueprint(v2)


def add_deprecation_headers(response, deprecated_prefix: str = "/api/v0"):
    """Add Deprecation header to old API responses."""
    if response and hasattr(response, "headers"):
        from flask import request
        if request.path.startswith(deprecated_prefix):
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"]      = "2026-01-01"
            response.headers["Link"]        = '</api/v1>; rel="successor-version"'
    return response
