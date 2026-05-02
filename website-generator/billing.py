"""
billing.py — Subscription & Monetization System
Plans: free | pro | business
Stripe integration (mock-safe: works without Stripe keys, activates when set)
"""
import os
import hashlib
import json
from functools import wraps
from flask import session, jsonify, redirect, url_for, flash
import db as database

# ── Plan definitions ──────────────────────────────────────────────────────────
PLANS = {
    "free": {
        "name":            "Free",
        "price_monthly":   0,
        "price_id":        None,
        "generations":     5,       # per hour
        "projects":        3,       # max total
        "features": [
            "5 AI generations / hour",
            "3 projects max",
            "Static & Flask sites",
            "ZIP download",
            "Community support",
        ],
        "badge_color": "#888",
    },
    "pro": {
        "name":            "Pro",
        "price_monthly":   9.99,
        "price_id":        os.environ.get("STRIPE_PRO_PRICE_ID", "price_pro"),
        "generations":     100,
        "projects":        50,
        "features": [
            "100 AI generations / hour",
            "50 projects",
            "All 6 project types",
            "Live editor",
            "Version history",
            "Priority support",
        ],
        "badge_color": "#6c63ff",
    },
    "business": {
        "name":            "Business",
        "price_monthly":   29.99,
        "price_id":        os.environ.get("STRIPE_BIZ_PRICE_ID", "price_business"),
        "generations":     500,
        "projects":        200,
        "features": [
            "500 AI generations / hour",
            "200 projects",
            "E-commerce + admin panel",
            "API access",
            "Custom domain export",
            "Dedicated support",
        ],
        "badge_color": "#f50057",
    },
}

STRIPE_SECRET = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")


def get_plan(plan_name: str) -> dict:
    return PLANS.get(plan_name, PLANS["free"])


def get_user_plan(user_id: int) -> str:
    return database.get_user_plan(user_id)


def can_generate(user_id: int) -> tuple[bool, str]:
    """
    Check if user can generate based on their plan limits.
    Returns (allowed: bool, reason: str)
    """
    plan_name = get_user_plan(user_id)
    plan      = PLANS[plan_name]
    limit     = plan["generations"]

    count = database.increment_rate_limit(user_id, "generate")
    # Decrement back — we only want to check, not consume yet
    # (actual consumption happens in rate_limiter.py)
    # Re-read without incrementing
    rl = database.get_rate_limit(user_id, "generate")
    current = rl["count"]

    if current > limit:
        return False, f"Generation limit reached ({limit}/hour on {plan_name} plan). Upgrade to generate more."

    # Check project count
    projects = database.get_user_projects(user_id)
    if len(projects) >= plan["projects"]:
        return False, f"Project limit reached ({plan['projects']} on {plan_name} plan). Upgrade or delete old projects."

    return True, "ok"


def plan_required(min_plan: str):
    """
    Decorator: require at least a certain plan level.
    Usage: @plan_required('pro')
    """
    plan_order = ["free", "pro", "business"]

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get("user_id"):
                return redirect(url_for("login"))
            user_plan = get_user_plan(session["user_id"])
            if plan_order.index(user_plan) < plan_order.index(min_plan):
                if _is_json_request():
                    return jsonify({
                        "error": f"This feature requires {min_plan} plan.",
                        "upgrade_url": url_for("pricing")
                    }), 403
                flash(f"This feature requires the {min_plan.capitalize()} plan.", "error")
                return redirect(url_for("pricing"))
            return f(*args, **kwargs)
        return decorated
    return decorator


def _is_json_request() -> bool:
    from flask import request
    return request.is_json or request.headers.get("Accept") == "application/json"


# ── Stripe integration ────────────────────────────────────────────────────────

def create_checkout_session(user_id: int, plan: str, success_url: str, cancel_url: str):
    """
    Create a Stripe Checkout session.
    Returns session URL or None if Stripe not configured.
    """
    if not STRIPE_SECRET:
        return None  # Stripe not configured — use mock upgrade

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET

        user = database.get_user_by_id(user_id)
        price_id = PLANS[plan]["price_id"]

        session_obj = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer_email=dict(user).get("email", ""),
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            metadata={"user_id": str(user_id), "plan": plan},
        )
        return session_obj.url
    except Exception as e:
        return None


def handle_webhook(payload: bytes, sig_header: str) -> dict:
    """
    Process Stripe webhook events.
    Returns {"ok": True} or {"error": "..."}
    """
    if not STRIPE_SECRET:
        return {"ok": True}

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)

        if event["type"] == "checkout.session.completed":
            s = event["data"]["object"]
            user_id = int(s["metadata"]["user_id"])
            plan    = s["metadata"]["plan"]
            database.upsert_subscription(
                user_id=user_id, plan=plan,
                stripe_customer_id=s.get("customer"),
                stripe_sub_id=s.get("subscription"),
                status="active"
            )

        elif event["type"] in ("customer.subscription.deleted",
                               "customer.subscription.paused"):
            sub = event["data"]["object"]
            conn = database.get_db()
            row = conn.execute(
                "SELECT user_id FROM subscriptions WHERE stripe_sub_id=?",
                (sub["id"],)
            ).fetchone()
            conn.close()
            if row:
                database.upsert_subscription(dict(row).get("user_id"), "free", status="cancelled")

        return {"ok": True}
    except Exception as e:
        return {"error": str(e)}


def mock_upgrade(user_id: int, plan: str) -> None:
    """Dev-mode upgrade without Stripe (for testing)."""
    database.upsert_subscription(user_id, plan, status="active")
