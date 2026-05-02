"""
utils/health.py — Health check endpoints for load balancers and monitoring
"""
import os
import time
import sqlite3
from pathlib import Path
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

_start_time = time.time()


@health_bp.route("/health")
def health():
    """
    Basic health check — returns 200 if app is running.
    Used by Render, Railway, AWS ALB, etc.
    """
    return jsonify({
        "status":  "ok",
        "service": "WebGen SaaS",
        "version": os.environ.get("APP_VERSION", "2.0.0"),
    }), 200


@health_bp.route("/health/ready")
def readiness():
    """
    Readiness check — verifies DB connectivity.
    Returns 503 if not ready to serve traffic.
    """
    checks = {}

    # Check database
    try:
        db_path = os.environ.get("SQLITE_PATH",
                  str(Path(__file__).parent.parent / "platform.db"))
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")
        conn.close()
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    # Check generated dir
    gen_dir = Path(__file__).parent.parent / "generated"
    checks["storage"] = "ok" if gen_dir.exists() else "missing"

    all_ok = all(v == "ok" for v in checks.values())
    return jsonify({
        "status": "ready" if all_ok else "not_ready",
        "checks": checks,
    }), 200 if all_ok else 503


@health_bp.route("/health/live")
def liveness():
    """
    Liveness check — verifies app hasn't deadlocked.
    Returns uptime and basic metrics.
    """
    uptime = round(time.time() - _start_time, 1)
    return jsonify({
        "status": "alive",
        "uptime_seconds": uptime,
    }), 200
