"""
app.py — WebGen SaaS Platform
Full Flask application: auth, wizard, NLP generation, project management,
live editor, admin panel, billing, rate limiting, analytics, API keys,
AI designer, content generator, SEO engine, chat builder, memory,
debugger, multi-framework export, plugins, marketplace, team collab.
"""
import os
import uuid
import json
import shutil
from pathlib import Path
from functools import wraps

from flask import (Flask, render_template, request, jsonify,
                   send_file, redirect, url_for, flash, session, g)
from werkzeug.security import generate_password_hash, check_password_hash

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import db as database
from generator import build_project, make_zip, read_file, project_exists
from nlp import parse_prompt, list_themes, get_theme
from codegen import generate_structured, slugify
from billing import PLANS, get_user_plan, can_generate, mock_upgrade, create_checkout_session, handle_webhook
from rate_limiter import check_generation_limit, generate_api_key, hash_api_key, api_key_required
from cache import get_cached, save_to_cache, is_minor_edit, compress_prompt, get_stats as cache_stats
from config import get_config
from utils.logger import setup_logging, log_request, get_logger
from utils.security import apply_security_headers, inject_csrf, auth_rate_limit, sanitize, sanitize_prompt, validate_email, validate_username
from utils.health import health_bp
from ai_engine.optimizer import PromptOptimizer
from ai_engine.validator import ResponseValidator
from ai_engine.designer  import get_design_decision, apply_design_to_config
from ai_engine.content   import ContentGenerator
from ai_engine.seo       import enhance_project_files, get_lighthouse_hints
from ai_engine.memory    import learn_from_generation, get_personalized_defaults, get_suggestions
from ai_engine.chat      import ChatBuilder
from ai_engine.debugger  import AIDebugger
from ai_engine.exporter  import export_to_react, export_to_nextjs, SUPPORTED_FRAMEWORKS
from ai_engine.plugins   import get_all_plugins, inject_all_plugins, inject_plugin

# ── Bootstrap logging ─────────────────────────────────────────────────────────
cfg = get_config()
setup_logging(
    level       = cfg.LOG_LEVEL,
    json_output = os.environ.get("FLASK_ENV") == "production",
)
logger = get_logger("app")

app = Flask(__name__)
app.secret_key = cfg.SECRET_KEY

# ── Apply config ──────────────────────────────────────────────────────────────
app.config["MAX_CONTENT_LENGTH"] = cfg.MAX_CONTENT_LENGTH
app.config["SESSION_COOKIE_SECURE"]   = cfg.SESSION_COOKIE_SECURE
app.config["SESSION_COOKIE_HTTPONLY"] = cfg.SESSION_COOKIE_HTTPONLY
app.config["SESSION_COOKIE_SAMESITE"] = cfg.SESSION_COOKIE_SAMESITE

# ── Register middleware ───────────────────────────────────────────────────────
apply_security_headers(app)
inject_csrf(app)
log_request(app)

# ── Register blueprints ───────────────────────────────────────────────────────
app.register_blueprint(health_bp)

# Register new blueprint-based routes (auth, dashboard, generate, etc.)
try:
    from app.routes.auth      import auth_bp
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
except Exception as _bp_err:
    pass  # blueprints optional — old routes still work

# ── AI engine singletons ──────────────────────────────────────────────────────
_optimizer   = PromptOptimizer()
_validator   = ResponseValidator()
_content_gen = ContentGenerator()
_debugger    = AIDebugger()
_chat        = ChatBuilder()

# ── Jinja filters ─────────────────────────────────────────────────────────────
@app.template_filter("from_json")
def from_json_filter(s):
    try:
        return json.loads(s)
    except Exception:
        return {}

GENERATED_DIR = Path(os.path.dirname(__file__)) / "generated"
GENERATED_DIR.mkdir(exist_ok=True)


# ── Bootstrap ─────────────────────────────────────────────────────────────────

@app.before_request
def setup():
    """Initialise DB tables on first request."""
    database.init_db()


# ── Decorators ────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please login to continue.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        user = database.get_user_by_id(session["user_id"])
        if not user or not user["is_admin"]:
            flash("Admin access required.", "error")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = database.get_user_by_username(username)
        if user and check_password_hash(user["password"], password):
            user_dict = dict(user)
            session["user_id"]  = user_dict["id"]
            session["username"] = user_dict["username"]
            session["is_admin"] = bool(user_dict.get("is_admin", 0))
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = sanitize(request.form.get("username", ""), 30).strip()
        email    = sanitize(request.form.get("email", ""), 100).strip()
        pwd      = request.form.get("password", "")

        valid_u, err_u = validate_username(username)
        if not valid_u:
            flash(err_u, "error")
            return render_template("signup.html")
        if not validate_email(email):
            flash("Please enter a valid email address.", "error")
            return render_template("signup.html")
        if len(pwd) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("signup.html")
        if database.create_user(username, email, generate_password_hash(pwd)):
            logger.info("New user registered: %s", username)
            flash("Account created! Please login.", "success")
            return redirect(url_for("login"))
        flash("Username or email already exists.", "error")
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """User account settings — change password."""
    if request.method == "POST":
        current  = request.form.get("current_password", "")
        new_pwd  = request.form.get("new_password", "")
        user = database.get_user_by_id(session["user_id"])
        if not check_password_hash(user["password"], current):
            flash("Current password is incorrect.", "error")
        elif len(new_pwd) < 6:
            flash("New password must be at least 6 characters.", "error")
        else:
            database.update_user_password(session["user_id"], generate_password_hash(new_pwd))
            flash("Password updated successfully.", "success")
    user = database.get_user_by_id(session["user_id"])
    projects = database.get_user_projects(session["user_id"])
    return render_template("account.html", user=user, project_count=len(projects))


# ── Public landing ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    themes = list_themes()
    return render_template("index.html", themes=themes)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    projects = database.get_user_projects(session["user_id"])
    return render_template("dashboard.html", projects=projects)


# ── NLP Quick Generate (prompt box on dashboard) ──────────────────────────────

@app.route("/quick-generate", methods=["GET", "POST"])
@login_required
def quick_generate():
    """
    Accepts a natural language prompt, parses it, generates the site,
    and redirects to the editor.
    """
    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if not prompt:
            flash("Please enter a description.", "error")
            return redirect(url_for("dashboard"))

        config = parse_prompt(prompt)
        session["wiz_config"] = config
        # Pre-fill wizard session so user can refine in step3
        session["wiz_type"]  = config["website_type"]
        session["wiz_stack"] = config["project_type"]
        return redirect(url_for("wizard_step3"))

    return render_template("quick_generate.html", themes=list_themes())


# ── Wizard ────────────────────────────────────────────────────────────────────

@app.route("/wizard/step1")
@login_required
def wizard_step1():
    return render_template("wizard/step1.html")


@app.route("/wizard/step2", methods=["GET", "POST"])
@login_required
def wizard_step2():
    if request.method == "POST":
        session["wiz_type"]  = request.form.get("website_type", "business")
        session["wiz_stack"] = request.form.get("stack", "static")
    return render_template("wizard/step2.html",
                           wiz_type=session.get("wiz_type", "business"),
                           wiz_stack=session.get("wiz_stack", "static"),
                           themes=list_themes())


@app.route("/wizard/step3", methods=["GET", "POST"])
@login_required
def wizard_step3():
    if request.method == "POST":
        wtype = session.get("wiz_type", "business")
        stack = session.get("wiz_stack", "static")
        session["wiz_config"] = {
            "site_name":       request.form.get("site_name", "My Website"),
            "tagline":         request.form.get("tagline", ""),
            "primary_color":   request.form.get("primary_color", "#6c63ff"),
            "secondary_color": request.form.get("secondary_color", "#f50057"),
            "font":            request.form.get("font", "Poppins"),
            "sections":        request.form.getlist("sections"),
            "has_auth":        "has_auth" in request.form,
            "has_db":          "has_db" in request.form,
            "website_type":    wtype,
            "project_type":    _resolve_project_type(stack, wtype),
        }
    config = session.get("wiz_config", {})
    return render_template("wizard/step3.html", config=config)


def _resolve_project_type(stack: str, wtype: str) -> str:
    if wtype == "ecommerce":
        return "ecommerce"
    if stack in ("flask", "fullstack"):
        return "flask"
    return "static"


# ── Generate API ──────────────────────────────────────────────────────────────

@app.route("/api/generate", methods=["POST"])
@login_required
def api_generate():
    """POST JSON: { config: {...} } — Returns: { project_id, files, type }"""
    data   = request.get_json(silent=True) or {}
    config = data.get("config") or session.get("wiz_config", {})

    if not config:
        return jsonify({"error": "No configuration provided."}), 400

    project_id = str(uuid.uuid4())[:8]

    try:
        result = build_project(project_id, config)

        database.save_project(
            project_id   = project_id,
            user_id      = session["user_id"],
            name         = config.get("site_name", "My Project"),
            website_type = config.get("website_type", "business"),
            prompt       = config.get("prompt") or config.get("tagline", ""),
            config       = json.dumps(config),
            project_type = result["type"],
        )
        database.log_event(session["user_id"], project_id, "generate",
                           {"type": result["type"]})

        return jsonify({
            "project_id": project_id,
            "files":      result["files"],
            "type":       result["type"],
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/prompt-generate", methods=["POST"])
@login_required
def api_prompt_generate():
    """Parse a natural language prompt and generate a site in one call."""
    data   = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400

    config     = parse_prompt(prompt)
    project_id = str(uuid.uuid4())[:8]

    try:
        result = build_project(project_id, config)
        database.save_project(
            project_id   = project_id,
            user_id      = session["user_id"],
            name         = config.get("site_name", "My Project"),
            website_type = config.get("website_type", "business"),
            prompt       = prompt,
            config       = json.dumps(config),
            project_type = result["type"],
        )
        database.log_event(session["user_id"], project_id, "prompt_generate",
                           {"prompt": prompt[:100]})
        return jsonify({
            "project_id": project_id,
            "files":      result["files"],
            "type":       result["type"],
            "config":     config,
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ── Live editor ───────────────────────────────────────────────────────────────

@app.route("/editor/<project_id>")
@login_required
def editor(project_id):
    """Visual live editor for a generated project."""
    project = database.get_project(project_id)
    if not project or project["user_id"] != session["user_id"]:
        flash("Project not found.", "error")
        return redirect(url_for("dashboard"))

    config   = json.loads(project["config"] or "{}")
    versions = database.get_versions(project_id)
    themes   = list_themes()
    return render_template("editor.html",
                           project=project, config=config,
                           versions=versions, themes=themes)


@app.route("/api/editor/save", methods=["POST"])
@login_required
def api_editor_save():
    """Save edited config and regenerate the project files."""
    data       = request.get_json(silent=True) or {}
    project_id = data.get("project_id")
    config     = data.get("config", {})

    if not project_id or not config:
        return jsonify({"error": "Missing project_id or config."}), 400

    project = database.get_project(project_id)
    if not project or project["user_id"] != session["user_id"]:
        return jsonify({"error": "Project not found."}), 404

    try:
        # Save version snapshot before overwriting
        database.save_version(project_id, project["config"], label="auto-save")

        # Regenerate files
        result = build_project(project_id, config)

        # Update DB
        database.update_project_config(
            project_id, session["user_id"],
            config.get("site_name", project["name"]),
            json.dumps(config)
        )
        database.log_event(session["user_id"], project_id, "editor_save", {})

        return jsonify({"ok": True, "files": result["files"]})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/editor/preview", methods=["POST"])
@login_required
def api_editor_preview():
    """Return inline HTML preview for a config without saving."""
    data   = request.get_json(silent=True) or {}
    config = data.get("config", {})
    if not config:
        return jsonify({"error": "No config."}), 400

    tmp_id = "preview_" + str(uuid.uuid4())[:6]
    try:
        build_project(tmp_id, config)
        html = read_file(tmp_id, "index.html") or ""
        css  = read_file(tmp_id, "style.css")  or ""
        js   = read_file(tmp_id, "script.js")  or ""
        html = html.replace('<link rel="stylesheet" href="style.css"/>',
                            f"<style>{css}</style>")
        html = html.replace('<script src="script.js"></script>',
                            f"<script>{js}</script>")
        # Clean up temp
        tmp_path = GENERATED_DIR / tmp_id
        if tmp_path.exists():
            shutil.rmtree(tmp_path)
        return jsonify({"html": html})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ── Project management ────────────────────────────────────────────────────────

@app.route("/project/duplicate/<project_id>", methods=["POST"])
@login_required
def duplicate_project(project_id):
    new_id = str(uuid.uuid4())[:8]
    if database.duplicate_project(project_id, session["user_id"], new_id):
        # Copy generated files if they exist
        src = GENERATED_DIR / project_id
        dst = GENERATED_DIR / new_id
        if src.exists():
            shutil.copytree(src, dst)
        flash("Project duplicated.", "success")
    else:
        flash("Could not duplicate project.", "error")
    return redirect(url_for("dashboard"))


@app.route("/project/rename/<project_id>", methods=["POST"])
@login_required
def rename_project(project_id):
    new_name = request.form.get("name", "").strip()
    if new_name and database.rename_project(project_id, session["user_id"], new_name):
        return jsonify({"ok": True})
    return jsonify({"error": "Could not rename."}), 400


@app.route("/project/delete/<project_id>", methods=["POST"])
@login_required
def delete_project(project_id):
    database.delete_project(project_id, session["user_id"])
    # Remove generated files
    proj_path = GENERATED_DIR / project_id
    if proj_path.exists():
        shutil.rmtree(proj_path)
    flash("Project deleted.", "success")
    return redirect(url_for("dashboard"))


@app.route("/project/versions/<project_id>")
@login_required
def project_versions(project_id):
    project  = database.get_project(project_id)
    if not project or project["user_id"] != session["user_id"]:
        flash("Project not found.", "error")
        return redirect(url_for("dashboard"))
    versions = database.get_versions(project_id)
    return render_template("versions.html", project=project, versions=versions)


@app.route("/api/version/restore", methods=["POST"])
@login_required
def restore_version():
    data       = request.get_json(silent=True) or {}
    project_id = data.get("project_id")
    config_str = data.get("config")
    if not project_id or not config_str:
        return jsonify({"error": "Missing data."}), 400
    project = database.get_project(project_id)
    if not project or project["user_id"] != session["user_id"]:
        return jsonify({"error": "Not found."}), 404
    try:
        config = json.loads(config_str)
        build_project(project_id, config)
        database.update_project_config(project_id, session["user_id"],
                                       config.get("site_name", project["name"]),
                                       config_str)
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ── File viewer ───────────────────────────────────────────────────────────────

@app.route("/file/<project_id>/<path:filepath>")
@login_required
def view_file(project_id, filepath):
    content = read_file(project_id, filepath)
    if content is None:
        return "File not found", 404
    return content, 200, {"Content-Type": "text/plain; charset=utf-8"}


# ── Preview ───────────────────────────────────────────────────────────────────

@app.route("/preview/<project_id>")
@login_required
def preview(project_id):
    project = database.get_project(project_id)
    if not project or project["user_id"] != session["user_id"]:
        flash("Project not found.", "error")
        return redirect(url_for("dashboard"))

    if project["project_type"] == "static":
        html = read_file(project_id, "index.html") or ""
        css  = read_file(project_id, "style.css")  or ""
        js   = read_file(project_id, "script.js")  or ""
        html = html.replace('<link rel="stylesheet" href="style.css"/>',
                            f"<style>{css}</style>")
        html = html.replace('<script src="script.js"></script>',
                            f"<script>{js}</script>")
        return html

    return render_template("preview.html", project=project)


# ── Download ──────────────────────────────────────────────────────────────────

@app.route("/download/<project_id>")
@login_required
def download(project_id):
    project = database.get_project(project_id)
    if not project or project["user_id"] != session["user_id"]:
        flash("Project not found.", "error")
        return redirect(url_for("dashboard"))
    if not project_exists(project_id):
        flash("Project files not found. Please regenerate.", "error")
        return redirect(url_for("dashboard"))
    zip_path = make_zip(project_id)
    database.log_event(session["user_id"], project_id, "download", {})
    return send_file(zip_path, as_attachment=True,
                     download_name=f"{project['name'].replace(' ','_')}.zip")


# ── Theme API ─────────────────────────────────────────────────────────────────

@app.route("/api/themes")
def api_themes():
    return jsonify(list_themes())


@app.route("/api/theme/<name>")
def api_theme(name):
    return jsonify(get_theme(name))


# ── Admin panel ───────────────────────────────────────────────────────────────

@app.route("/admin")
@admin_required
def admin():
    stats = database.get_platform_stats()
    users = database.get_all_users()
    return render_template("admin/index.html", stats=stats, users=users)


@app.route("/admin/user/delete/<int:user_id>", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    if user_id == session["user_id"]:
        flash("Cannot delete your own account.", "error")
    else:
        database.delete_user(user_id)
        flash("User deleted.", "success")
    return redirect(url_for("admin"))


@app.route("/admin/make-admin/<int:user_id>", methods=["POST"])
@admin_required
def admin_make_admin(user_id):
    conn = database.get_db()
    conn.execute("UPDATE users SET is_admin=1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    flash("User promoted to admin.", "success")
    return redirect(url_for("admin"))


# ── Code Generation Engine (structured output) ───────────────────────────────

@app.route("/generate", methods=["GET", "POST"])
@login_required
def generate_page():
    """
    The main code generation page.
    GET  → show the prompt input UI
    POST → parse prompt, optimize, generate, validate, show structured output
    """
    if request.method == "POST":
        raw_prompt = request.form.get("prompt", "").strip()
        prompt     = sanitize_prompt(raw_prompt)
        if not prompt:
            flash("Please enter a prompt.", "error")
            return render_template("generate.html", themes=list_themes())

        # Rate limit check
        allowed, msg = check_generation_limit(session["user_id"])
        if not allowed:
            flash(msg, "error")
            return redirect(url_for("pricing"))

        # Optimize prompt
        optimized  = _optimizer.optimize(prompt)
        project_id = str(uuid.uuid4())[:8]
        try:
            result = generate_structured(optimized, project_id)

            # Validate output
            validation = _validator.validate(result["files"], result["type"])
            if not validation["valid"]:
                logger.error("Validation failed: %s", validation["errors"])
                flash("Generation produced invalid output. Please try again.", "error")
                return render_template("generate.html", themes=list_themes())

            database.save_project(
                project_id   = project_id,
                user_id      = session["user_id"],
                name         = result["site_name"],
                website_type = result["website_type"],
                prompt       = prompt,
                config       = json.dumps(result["config"]),
                project_type = result["type"],
            )
            database.log_event(session["user_id"], project_id,
                               "codegen", {"prompt": prompt[:100]})
            database.increment_rate_limit(session["user_id"], "generate")
            logger.info("Generated %s project %s for user %s",
                        result["type"], project_id, session["user_id"])
            return render_template("generate_output.html",
                                   result=result, prompt=prompt,
                                   validation=validation)
        except Exception as exc:
            logger.exception("Generation failed: %s", exc)
            flash(f"Generation failed: {exc}", "error")
            return render_template("generate.html", themes=list_themes())

    return render_template("generate.html", themes=list_themes())


@app.route("/api/generate-structured", methods=["POST"])
@login_required
def api_generate_structured():
    """
    JSON API: POST { prompt: "..." }
    Returns full structured output with all file contents.
    """
    data   = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    project_id = str(uuid.uuid4())[:8]
    try:
        result = generate_structured(prompt, project_id)

        database.save_project(
            project_id   = project_id,
            user_id      = session["user_id"],
            name         = result["site_name"],
            website_type = result["website_type"],
            prompt       = prompt,
            config       = json.dumps(result["config"]),
            project_type = result["type"],
        )
        database.log_event(session["user_id"], project_id,
                           "api_codegen", {"prompt": prompt[:100]})

        return jsonify({
            "ok":               True,
            "project_id":       result["project_id"],
            "project_name":     result["project_name"],
            "site_name":        result["site_name"],
            "type":             result["type"],
            "website_type":     result["website_type"],
            "theme":            result["theme"],
            "folder_structure": result["folder_structure"],
            "folder_tree":      result["folder_tree"],
            "files":            result["files"],
            "run_instructions": result["run_instructions"],
            "summary":          result["summary"],
            "total_files":      result["total_files"],
            "total_lines":      result["total_lines"],
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ── Pricing ───────────────────────────────────────────────────────────────────

@app.route("/pricing")
def pricing():
    user_plan  = get_user_plan(session["user_id"]) if session.get("user_id") else "free"
    stripe_pub = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
    return render_template("pricing.html", plans=PLANS, user_plan=user_plan,
                           stripe_pub=stripe_pub)


# ── Billing ───────────────────────────────────────────────────────────────────

@app.route("/billing/checkout/<plan>", methods=["POST"])
@login_required
def billing_checkout(plan):
    if plan not in PLANS or plan == "free":
        flash("Invalid plan.", "error")
        return redirect(url_for("pricing"))
    if not os.environ.get("STRIPE_SECRET_KEY"):
        mock_upgrade(session["user_id"], plan)
        flash(f"✅ Upgraded to {plan.capitalize()} plan! (dev mode)", "success")
        return redirect(url_for("billing_portal"))
    checkout_url = create_checkout_session(
        user_id     = session["user_id"],
        plan        = plan,
        success_url = request.host_url.rstrip("/") + url_for("billing_success"),
        cancel_url  = request.host_url.rstrip("/") + url_for("pricing"),
    )
    if checkout_url:
        return redirect(checkout_url)
    flash("Payment system unavailable.", "error")
    return redirect(url_for("pricing"))


@app.route("/billing/success")
@login_required
def billing_success():
    flash("Payment successful! Your plan has been upgraded.", "success")
    return redirect(url_for("billing_portal"))


@app.route("/billing")
@login_required
def billing_portal():
    user_plan = get_user_plan(session["user_id"])
    plan_info = PLANS[user_plan]
    sub       = database.get_subscription(session["user_id"])
    api_keys  = database.get_user_api_keys(session["user_id"])
    new_key   = session.pop("new_api_key", None)
    return render_template("billing.html", plan=user_plan, plan_info=plan_info,
                           sub=sub, api_keys=api_keys, plans=PLANS, new_key=new_key)


@app.route("/billing/downgrade", methods=["POST"])
@login_required
def billing_downgrade():
    mock_upgrade(session["user_id"], "free")
    flash("Downgraded to Free plan.", "success")
    return redirect(url_for("billing_portal"))


@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    result = handle_webhook(request.get_data(),
                            request.headers.get("Stripe-Signature", ""))
    return (jsonify({"ok": True}) if result.get("ok")
            else (jsonify({"error": result.get("error")}), 400))


# ── API key management ────────────────────────────────────────────────────────

@app.route("/api-keys/create", methods=["POST"])
@login_required
def create_api_key_route():
    name = request.form.get("name", "Default").strip()
    raw, hashed, prefix = generate_api_key()
    database.create_api_key(session["user_id"], hashed, prefix, name)
    session["new_api_key"] = raw
    return redirect(url_for("billing_portal"))


@app.route("/api-keys/delete/<int:key_id>", methods=["POST"])
@login_required
def delete_api_key_route(key_id):
    database.delete_api_key(key_id, session["user_id"])
    flash("API key deleted.", "success")
    return redirect(url_for("billing_portal"))


# ── Public REST API (API key auth) ────────────────────────────────────────────

@app.route("/api/v1/generate", methods=["POST"])
@api_key_required
def api_v1_generate():
    """Public API — requires Bearer API key. POST { prompt: '...' }"""
    user_id = g.api_user_id
    data    = request.get_json(silent=True) or {}
    prompt  = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400
    allowed, msg = check_generation_limit(user_id)
    if not allowed:
        return jsonify({"error": msg}), 429
    cached = get_cached(prompt)
    if cached:
        return jsonify({"ok": True, "cached": True, **cached})
    project_id = str(uuid.uuid4())[:8]
    try:
        result = generate_structured(prompt, project_id)
        database.save_project(project_id=project_id, user_id=user_id,
                              name=result["site_name"], website_type=result["website_type"],
                              prompt=prompt, config=json.dumps(result["config"]),
                              project_type=result["type"])
        database.log_event(user_id, project_id, "api_v1_generate", {"prompt": prompt[:80]})
        database.increment_rate_limit(user_id, "generate")
        save_to_cache(prompt, result["config"], {
            "project_id": result["project_id"], "project_name": result["project_name"],
            "type": result["type"], "folder_tree": result["folder_tree"],
            "run_instructions": result["run_instructions"],
            "total_files": result["total_files"], "total_lines": result["total_lines"],
        })
        return jsonify({"ok": True, "cached": False,
                        "project_id": project_id, "project_name": result["project_name"],
                        "type": result["type"], "total_files": result["total_files"],
                        "total_lines": result["total_lines"],
                        "folder_tree": result["folder_tree"],
                        "run_instructions": result["run_instructions"],
                        "files": result["files"]})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ── Admin analytics ───────────────────────────────────────────────────────────

@app.route("/admin/analytics")
@admin_required
def admin_analytics():
    analytics = database.get_full_analytics()
    c_stats   = cache_stats()
    stats     = database.get_platform_stats()
    return render_template("admin/analytics.html",
                           analytics=analytics, cache=c_stats, stats=stats)


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE 1 — Smart AI Designer: auto design decisions per prompt
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/design-decision", methods=["POST"])
@login_required
def api_design_decision():
    """Return AI design decisions (colors, fonts, layout) for a prompt."""
    data   = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "prompt required"}), 400
    decision = get_design_decision(prompt)
    return jsonify({"ok": True, "decision": decision})


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE 2 — AI Content Generator
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/generate-content", methods=["POST"])
@login_required
def api_generate_content():
    """Generate website copy for all sections."""
    data         = request.get_json(silent=True) or {}
    site_name    = data.get("site_name", "My Website")
    industry     = data.get("industry", "default")
    website_type = data.get("website_type", "business")
    language     = data.get("language", "en")
    content = _content_gen.generate(site_name, industry, website_type, language)
    return jsonify({"ok": True, "content": content})


@app.route("/api/rewrite-text", methods=["POST"])
@login_required
def api_rewrite_text():
    """Rewrite a piece of text with AI (inline editor)."""
    data        = request.get_json(silent=True) or {}
    text        = data.get("text", "").strip()
    tone        = data.get("tone", "professional")
    instruction = data.get("instruction", "")
    if not text:
        return jsonify({"error": "text required"}), 400
    rewritten = _content_gen.rewrite_text(text, tone, instruction)
    return jsonify({"ok": True, "rewritten": rewritten})


# ── Blog post generator ───────────────────────────────────────────────────────

@app.route("/api/generate-blog-post", methods=["POST"])
@login_required
def api_generate_blog_post():
    data     = request.get_json(silent=True) or {}
    topic    = data.get("topic", "").strip()
    industry = data.get("industry", "default")
    if not topic:
        return jsonify({"error": "topic required"}), 400
    post = _content_gen.generate_blog_post(topic, industry)
    return jsonify({"ok": True, "post": post})


# ── SEO enhancement ───────────────────────────────────────────────────────────

@app.route("/api/seo-enhance/<project_id>", methods=["POST"])
@login_required
def api_seo_enhance(project_id):
    """Enhance a generated project with SEO meta tags, sitemap, robots.txt."""
    project = database.get_project(project_id)
    if not project or project["user_id"] != session["user_id"]:
        return jsonify({"error": "Project not found"}), 404
    config = json.loads(project["config"] or "{}")
    site_url = request.get_json(silent=True, force=True).get("site_url", "https://example.com") if request.data else "https://example.com"
    try:
        from generator import GENERATED_DIR
        proj_path = GENERATED_DIR / project_id
        files = {}
        for f in proj_path.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(proj_path))
                files[rel] = f.read_text(encoding="utf-8")
        enhanced = enhance_project_files(files, config, site_url)
        for filepath, content in enhanced.items():
            full = proj_path / filepath
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
        hints = get_lighthouse_hints(config.get("project_type", "static"))
        return jsonify({"ok": True, "hints": hints, "added_files": ["sitemap.xml", "robots.txt"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── AI Chat Builder ───────────────────────────────────────────────────────────

@app.route("/chat")
@login_required
def chat_builder():
    """Conversational website builder UI."""
    defaults = get_personalized_defaults(session["user_id"])
    return render_template("chat.html", defaults=defaults)


@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    """Process a chat message and return AI response."""
    data    = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    state   = data.get("state", {})
    if not message:
        return jsonify({"error": "message required"}), 400
    result = _chat.process_message(message, state)
    return jsonify(result)


@app.route("/api/chat/generate", methods=["POST"])
@login_required
def api_chat_generate():
    """Generate a project from a completed chat config."""
    data   = request.get_json(silent=True) or {}
    config = data.get("config", {})
    if not config:
        return jsonify({"error": "config required"}), 400
    allowed, msg = check_generation_limit(session["user_id"])
    if not allowed:
        return jsonify({"error": msg, "upgrade_url": "/pricing"}), 429
    project_id = str(uuid.uuid4())[:8]
    try:
        result = generate_structured(config.get("prompt", "website"), project_id)
        database.save_project(project_id=project_id, user_id=session["user_id"],
                              name=config.get("site_name", result["site_name"]),
                              website_type=result["website_type"], prompt=config.get("prompt",""),
                              config=json.dumps(result["config"]), project_type=result["type"])
        database.log_event(session["user_id"], project_id, "chat_generate", {})
        database.increment_rate_limit(session["user_id"], "generate")
        learn_from_generation(session["user_id"], result["config"])
        return jsonify({"ok": True, "project_id": project_id, "type": result["type"],
                        "files": result["files"], "total_files": result["total_files"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── AI Debugger ───────────────────────────────────────────────────────────────

@app.route("/debug/<project_id>")
@login_required
def debug_project(project_id):
    """AI debugger page for a project."""
    project = database.get_project(project_id)
    if not project or project["user_id"] != session["user_id"]:
        flash("Project not found.", "error")
        return redirect(url_for("dashboard"))
    return render_template("debug.html", project=project)


@app.route("/api/debug/<project_id>", methods=["POST"])
@login_required
def api_debug(project_id):
    """Analyze a project for issues."""
    project = database.get_project(project_id)
    if not project or project["user_id"] != session["user_id"]:
        return jsonify({"error": "Not found"}), 404
    from app.services.file_service import FileService
    files_list = FileService.list_files(project_id)
    files = []
    for fp in files_list:
        code = read_file(project_id, fp)
        if code:
            ext = fp.rsplit(".", 1)[-1] if "." in fp else ""
            lang_map = {"html": "html", "css": "css", "js": "javascript", "py": "python"}
            files.append({"path": fp, "code": code, "language": lang_map.get(ext, "text"),
                          "lines": code.count("\n") + 1})
    result = _debugger.analyze(files)
    return jsonify({"ok": True, **result})


@app.route("/api/debug/<project_id>/fix", methods=["POST"])
@login_required
def api_debug_fix(project_id):
    """Auto-fix detected issues in a project."""
    project = database.get_project(project_id)
    if not project or project["user_id"] != session["user_id"]:
        return jsonify({"error": "Not found"}), 404
    from app.services.file_service import FileService
    from generator import GENERATED_DIR
    files_list = FileService.list_files(project_id)
    files = []
    for fp in files_list:
        code = read_file(project_id, fp)
        if code:
            ext = fp.rsplit(".", 1)[-1] if "." in fp else ""
            lang_map = {"html": "html", "css": "css", "js": "javascript", "py": "python"}
            files.append({"path": fp, "code": code, "language": lang_map.get(ext, "text"),
                          "lines": code.count("\n") + 1})
    fixed = _debugger.fix(files)
    proj_path = GENERATED_DIR / project_id
    for f in fixed:
        full = proj_path / f["path"]
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(f["code"], encoding="utf-8")
    database.log_event(session["user_id"], project_id, "debug_fix", {})
    return jsonify({"ok": True, "fixed_files": len(fixed)})


# ── Plugin system ─────────────────────────────────────────────────────────────

@app.route("/api/plugins")
def api_plugins():
    """List all available plugins."""
    return jsonify(get_all_plugins())


@app.route("/api/plugins/<project_id>", methods=["GET"])
@login_required
def api_get_project_plugins(project_id):
    """Get plugins installed on a project."""
    project = database.get_project(project_id)
    if not project or project["user_id"] != session["user_id"]:
        return jsonify({"error": "Not found"}), 404
    conn = database.get_db()
    plugins = conn.execute("SELECT * FROM plugins WHERE project_id=?", (project_id,)).fetchall()
    conn.close()
    return jsonify([dict(p) for p in plugins])


@app.route("/api/plugins/<project_id>/install", methods=["POST"])
@login_required
def api_install_plugin(project_id):
    """Install a plugin on a project."""
    project = database.get_project(project_id)
    if not project or project["user_id"] != session["user_id"]:
        return jsonify({"error": "Not found"}), 404
    data        = request.get_json(silent=True) or {}
    plugin_type = data.get("plugin_type", "")
    config      = data.get("config", {})
    if plugin_type not in get_all_plugins():
        return jsonify({"error": "Unknown plugin"}), 400
    conn = database.get_db()
    conn.execute("INSERT OR REPLACE INTO plugins (project_id, plugin_type, config) VALUES (?,?,?)",
                 (project_id, plugin_type, json.dumps(config)))
    conn.commit()
    conn.close()
    database.log_event(session["user_id"], project_id, "plugin_install", {"type": plugin_type})
    return jsonify({"ok": True})


@app.route("/api/plugins/<project_id>/remove/<plugin_type>", methods=["DELETE"])
@login_required
def api_remove_plugin(project_id, plugin_type):
    project = database.get_project(project_id)
    if not project or project["user_id"] != session["user_id"]:
        return jsonify({"error": "Not found"}), 404
    conn = database.get_db()
    conn.execute("DELETE FROM plugins WHERE project_id=? AND plugin_type=?", (project_id, plugin_type))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


# ── Multi-framework export ────────────────────────────────────────────────────

@app.route("/api/export/<project_id>/<framework>")
@login_required
def api_export(project_id, framework):
    """Export a project to a different framework (react, nextjs, static)."""
    if framework not in SUPPORTED_FRAMEWORKS:
        return jsonify({"error": f"Unsupported framework. Choose: {SUPPORTED_FRAMEWORKS}"}), 400
    project = database.get_project(project_id)
    if not project or project["user_id"] != session["user_id"]:
        return jsonify({"error": "Not found"}), 404
    if framework == "static":
        return redirect(url_for("download", project_id=project_id))
    from app.services.file_service import FileService
    from generator import GENERATED_DIR
    import zipfile as zf
    files_list = FileService.list_files(project_id)
    source_files = {}
    for fp in files_list:
        code = read_file(project_id, fp)
        if code:
            source_files[fp] = code
    site_name = project["name"]
    if framework == "react":
        exported = export_to_react(source_files, site_name)
    else:
        exported = export_to_nextjs(source_files, site_name)
    export_id  = f"{project_id}_{framework}"
    export_dir = GENERATED_DIR / export_id
    export_dir.mkdir(parents=True, exist_ok=True)
    for filepath, content in exported.items():
        full = export_dir / filepath
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
    zip_path = GENERATED_DIR / f"{export_id}.zip"
    with zf.ZipFile(zip_path, "w", zf.ZIP_DEFLATED) as z:
        for f in export_dir.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(GENERATED_DIR))
    database.log_event(session["user_id"], project_id, f"export_{framework}", {})
    return send_file(zip_path, as_attachment=True,
                     download_name=f"{site_name}_{framework}.zip")


# ── Personalization ───────────────────────────────────────────────────────────

@app.route("/api/suggestions")
@login_required
def api_suggestions():
    """Get AI suggestions for the current user."""
    projects = database.get_user_projects(session["user_id"])
    suggestions = get_suggestions(session["user_id"], [dict(p) for p in projects])
    defaults    = get_personalized_defaults(session["user_id"])
    return jsonify({"suggestions": suggestions, "defaults": defaults})


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    database.init_db()
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"

    # ── Startup banner (only print once, not on reloader restart) ─────────
    import os as _os
    if not _os.environ.get("WERKZEUG_RUN_MAIN"):
        print()
        print("=" * 55)
        print("  ⚡  WebGen AI Website Builder")
        print("=" * 55)
        print(f"  🌐  Running on: http://127.0.0.1:{port}")
        print()
        print("  Pages:")
        print(f"    Home      →  http://127.0.0.1:{port}/")
        print(f"    Dashboard →  http://127.0.0.1:{port}/dashboard")
        print(f"    Generate  →  http://127.0.0.1:{port}/generate")
        print(f"    Chat AI   →  http://127.0.0.1:{port}/chat")
        print(f"    Pricing   →  http://127.0.0.1:{port}/pricing")
        print(f"    Admin     →  http://127.0.0.1:{port}/admin")
        print(f"    Health    →  http://127.0.0.1:{port}/health")
        print()
        print("  Press CTRL+C to stop")
        print("=" * 55)
        print()

    app.run(debug=debug, host="0.0.0.0", port=port, use_reloader=False, threaded=True)
