"""
rate_limiter.py — API Security Layer
- Per-user rate limiting (plan-aware)
- API key authentication
- Abuse prevention
"""
import os
import hashlib
import secrets
from functools import wraps
from flask import request, jsonify, session, g
import db as database
from billing import PLANS, get_user_plan

# ── Rate limit middleware ─────────────────────────────────────────────────────

def rate_limit(endpoint: str = None):
    """
    Decorator: enforce per-user rate limits based on their plan.
    Uses the 'generate' endpoint limit from PLANS.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_id = session.get("user_id") or getattr(g, "api_user_id", None)
            if not user_id:
                return jsonify({"error": "Authentication required."}), 401

            ep        = endpoint or request.endpoint or "default"
            plan_name = get_user_plan(user_id)
            plan      = PLANS[plan_name]
            limit     = plan["generations"]

            count = database.increment_rate_limit(user_id, ep)
            if count > limit:
                return jsonify({
                    "error": f"Rate limit exceeded ({limit}/hour on {plan_name} plan).",
                    "limit": limit,
                    "plan":  plan_name,
                    "upgrade_url": "/pricing",
                }), 429

            return f(*args, **kwargs)
        return decorated
    return decorator


def check_generation_limit(user_id: int) -> tuple[bool, str]:
    """
    Check generation + project limits without consuming a slot.
    Returns (allowed, message).
    """
    plan_name = get_user_plan(user_id)
    plan      = PLANS[plan_name]

    rl    = database.get_rate_limit(user_id, "generate")
    count = rl.get("count", 0)

    if count >= plan["generations"]:
        return False, (
            f"Rate limit: {plan['generations']}/hour on {plan_name} plan. "
            f"<a href='/pricing'>Upgrade</a> for more."
        )

    projects = database.get_user_projects(user_id)
    if len(projects) >= plan["projects"]:
        return False, (
            f"Project limit: {plan['projects']} on {plan_name} plan. "
            f"Delete old projects or <a href='/pricing'>upgrade</a>."
        )

    return True, "ok"


# ── API key authentication ────────────────────────────────────────────────────

def generate_api_key() -> tuple[str, str, str]:
    """
    Generate a new API key.
    Returns (raw_key, key_hash, key_prefix)
    raw_key is shown once to the user; only hash is stored.
    """
    raw    = "wg_" + secrets.token_urlsafe(32)
    prefix = raw[:10]
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed, prefix


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def api_key_required(f):
    """
    Decorator: authenticate via API key in Authorization header.
    Sets g.api_user_id on success.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer wg_"):
            return jsonify({"error": "API key required. Use: Authorization: Bearer wg_..."}), 401

        raw_key = auth.replace("Bearer ", "").strip()
        key_hash = hash_api_key(raw_key)
        key_row  = database.get_api_key(key_hash)

        if not key_row:
            return jsonify({"error": "Invalid API key."}), 401

        g.api_user_id = key_row["user_id"]
        return f(*args, **kwargs)
    return decorated


def login_or_api_key_required(f):
    """
    Decorator: accept either session login OR API key.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Try session first
        if session.get("user_id"):
            return f(*args, **kwargs)

        # Try API key
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer wg_"):
            raw_key  = auth.replace("Bearer ", "").strip()
            key_hash = hash_api_key(raw_key)
            key_row  = database.get_api_key(key_hash)
            if key_row:
                g.api_user_id = key_row["user_id"]
                return f(*args, **kwargs)

        return jsonify({"error": "Authentication required."}), 401
    return decorated
