"""
utils/security.py — Security middleware for WebGen SaaS
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- CSRF token generation and validation
- Input sanitization
- Auth rate limiting (brute-force protection)
"""
import os
import re
import hmac
import hashlib
import secrets
import time
from functools import wraps
from collections import defaultdict
from flask import request, session, jsonify, abort, g
from utils.logger import get_logger

logger = get_logger("security")

# ── Security headers ──────────────────────────────────────────────────────────

SECURITY_HEADERS = {
    "X-Content-Type-Options":    "nosniff",
    "X-Frame-Options":           "SAMEORIGIN",
    "X-XSS-Protection":          "1; mode=block",
    "Referrer-Policy":           "strict-origin-when-cross-origin",
    "Permissions-Policy":        "geolocation=(), microphone=(), camera=()",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}

CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://js.stripe.com https://fonts.googleapis.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data: https://picsum.photos https://i.pravatar.cc; "
    "connect-src 'self' https://api.stripe.com; "
    "frame-src https://js.stripe.com;"
)


def apply_security_headers(app):
    """Register after_request hook to add security headers."""

    @app.after_request
    def add_headers(response):
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        # Only add CSP in production (breaks inline scripts in dev)
        if os.environ.get("FLASK_ENV") == "production":
            response.headers["Content-Security-Policy"] = CSP
        return response

    return app


# ── CSRF protection ───────────────────────────────────────────────────────────

def generate_csrf_token() -> str:
    """Generate and store a CSRF token in the session."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def validate_csrf(token: str) -> bool:
    """Validate a CSRF token against the session."""
    stored = session.get("csrf_token", "")
    if not stored or not token:
        return False
    return hmac.compare_digest(stored, token)


def csrf_protect(f):
    """
    Decorator: validate CSRF token on state-changing requests.
    Skips JSON API requests (they use API key auth instead).
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            # Skip CSRF for JSON API requests (use API key auth)
            if request.is_json:
                return f(*args, **kwargs)
            # Skip for Stripe webhook
            if request.path == "/stripe/webhook":
                return f(*args, **kwargs)
            token = (request.form.get("csrf_token") or
                     request.headers.get("X-CSRF-Token", ""))
            if not validate_csrf(token):
                logger.warning("CSRF validation failed for %s %s",
                               request.method, request.path)
                abort(403)
        return f(*args, **kwargs)
    return decorated


def inject_csrf(app):
    """Make csrf_token available in all templates."""
    @app.context_processor
    def csrf_context():
        return {"csrf_token": generate_csrf_token()}
    return app


# ── Auth rate limiting (brute-force protection) ───────────────────────────────

# In-memory store: {ip: [(timestamp, count)]}
_auth_attempts: dict = defaultdict(list)
AUTH_LIMIT   = 10   # max attempts
AUTH_WINDOW  = 900  # 15 minutes


def check_auth_rate_limit(ip: str) -> bool:
    """
    Returns True if the IP is allowed to attempt auth.
    Returns False if rate limit exceeded.
    """
    now = time.time()
    attempts = _auth_attempts[ip]

    # Remove old attempts outside the window
    _auth_attempts[ip] = [t for t in attempts if now - t < AUTH_WINDOW]

    if len(_auth_attempts[ip]) >= AUTH_LIMIT:
        logger.warning("Auth rate limit exceeded for IP %s", ip)
        return False

    _auth_attempts[ip].append(now)
    return True


def auth_rate_limit(f):
    """Decorator: apply auth rate limiting to login/signup routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "POST":
            ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
            ip = ip.split(",")[0].strip()
            if not check_auth_rate_limit(ip):
                return jsonify({
                    "error": "Too many attempts. Please wait 15 minutes."
                }), 429
        return f(*args, **kwargs)
    return decorated


# ── Input sanitization ────────────────────────────────────────────────────────

# Characters that could cause XSS in HTML context
_DANGEROUS = re.compile(r"[<>\"'`]")


def sanitize(text: str, max_length: int = 500) -> str:
    """
    Basic input sanitization:
    - Strip leading/trailing whitespace
    - Remove dangerous HTML characters
    - Truncate to max_length
    """
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = _DANGEROUS.sub("", text)
    return text[:max_length]


def sanitize_prompt(prompt: str) -> str:
    """Sanitize a generation prompt — allow more characters but limit length."""
    if not isinstance(prompt, str):
        return ""
    prompt = prompt.strip()
    # Remove null bytes and control characters
    prompt = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", prompt)
    return prompt[:1000]


def validate_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email or ""))


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username format.
    Returns (valid: bool, error_message: str)
    """
    if not username:
        return False, "Username is required."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(username) > 30:
        return False, "Username must be 30 characters or less."
    if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens."
    return True, ""
