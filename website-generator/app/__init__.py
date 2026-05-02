"""
app/__init__.py — WebGen Application Factory
Creates and configures the Flask app with all blueprints registered.
"""
import os
import json
from flask import Flask
from pathlib import Path


def create_app(config: dict = None) -> Flask:
    """
    Application factory pattern.
    Usage:
        app = create_app()
        app.run()
    """
    # Resolve template/static paths relative to the project root (one level up)
    root = Path(__file__).parent.parent
    app = Flask(
        __name__,
        template_folder=str(root / "templates"),
        static_folder=str(root / "static"),
    )

    # ── Configuration ─────────────────────────────────────────────────────────
    app.secret_key = os.environ.get("SECRET_KEY", "webgen-saas-dev-2025")
    app.config["GENERATED_DIR"] = str(root / "generated")
    app.config["DB_PATH"]       = str(root / "platform.db")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload limit

    if config:
        app.config.update(config)

    # ── Jinja filters ─────────────────────────────────────────────────────────
    @app.template_filter("from_json")
    def from_json_filter(s):
        try:
            return json.loads(s)
        except Exception:
            return {}

    # ── Ensure generated dir exists ───────────────────────────────────────────
    Path(app.config["GENERATED_DIR"]).mkdir(exist_ok=True)

    # ── Register blueprints ───────────────────────────────────────────────────
    from app.routes.auth     import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.generate  import generate_bp
    from app.routes.editor    import editor_bp
    from app.routes.projects  import projects_bp
    from app.routes.admin     import admin_bp
    from app.routes.api       import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(generate_bp)
    app.register_blueprint(editor_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # ── Public landing ────────────────────────────────────────────────────────
    from flask import render_template
    from app.services.ai_engine import list_themes

    @app.route("/")
    def index():
        return render_template("index.html", themes=list_themes())

    # ── DB init on first request ──────────────────────────────────────────────
    import db as database

    @app.before_request
    def setup():
        database.init_db()

    return app
