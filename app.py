"""
app.py — Render.com WSGI entry point (repo root).

Gunicorn runs from repo root: gunicorn app:app
server.py uses Path(__file__).parent.parent to find build.py — works correctly
from any working directory because it's relative to server.py's own location.
"""
import sys
from pathlib import Path

# Ensure both builder dirs are on the path
_UI  = Path(__file__).parent / "static-site" / "builder" / "ui"
_BLD = Path(__file__).parent / "static-site" / "builder"
sys.path.insert(0, str(_UI))
sys.path.insert(0, str(_BLD))

# Import the Flask app from server.py
from server import app  # noqa: F401

__all__ = ["app"]
