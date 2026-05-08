"""wsgi.py — Render.com WSGI entry point."""
import os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault("SECRET_KEY", "dev-key-change-in-production")

from app import create_app

app = create_app()
application = app   # WSGI alias

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
