"""
utils/logger.py — Structured logging for WebGen SaaS
Outputs JSON in production, human-readable in development.
"""
import os
import sys
import json
import logging
import traceback
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter for production."""

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "ts":      datetime.now(timezone.utc).isoformat(),
            "level":   record.levelname,
            "logger":  record.name,
            "msg":     record.getMessage(),
            "module":  record.module,
            "line":    record.lineno,
        }
        if record.exc_info:
            log["exc"] = self.formatException(record.exc_info)
        if hasattr(record, "user_id"):
            log["user_id"] = record.user_id
        if hasattr(record, "project_id"):
            log["project_id"] = record.project_id
        if hasattr(record, "event"):
            log["event"] = record.event
        return json.dumps(log)


class DevFormatter(logging.Formatter):
    """Human-readable formatter for development."""
    COLORS = {
        "DEBUG":    "\033[36m",   # cyan
        "INFO":     "\033[32m",   # green
        "WARNING":  "\033[33m",   # yellow
        "ERROR":    "\033[31m",   # red
        "CRITICAL": "\033[35m",   # magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        ts    = datetime.now().strftime("%H:%M:%S")
        msg   = record.getMessage()
        base  = f"{color}[{ts}] {record.levelname:8} {record.name}: {msg}{self.RESET}"
        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)
        return base


def setup_logging(level: str = "INFO", json_output: bool = False) -> None:
    """
    Configure root logger.
    Call once at app startup.
    """
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter() if json_output else DevFormatter())
    root.addHandler(handler)

    # Silence noisy third-party loggers
    for noisy in ("werkzeug", "urllib3", "stripe"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)


# ── Request logging middleware ────────────────────────────────────────────────

def log_request(app):
    """Register before/after request hooks for access logging."""
    import time
    from flask import request, g

    logger = get_logger("access")

    @app.before_request
    def before():
        g._start_time = time.monotonic()

    @app.after_request
    def after(response):
        duration_ms = round((time.monotonic() - getattr(g, "_start_time", 0)) * 1000, 1)
        # Skip static files
        if not request.path.startswith("/static"):
            logger.info(
                "%s %s %s %.1fms",
                request.method, request.path, response.status_code, duration_ms
            )
        return response

    return app
