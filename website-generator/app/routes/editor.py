"""
app/routes/editor.py — Live Editor Blueprint
"""
import json
from flask import (Blueprint, render_template, request,
                   jsonify, redirect, url_for, flash, session)
from app.models.project import ProjectModel
from app.services.ai_engine import AIEngine, list_themes

editor_bp = Blueprint("editor", __name__)


def _login_required():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    return None


@editor_bp.route("/editor/<project_id>")
def editor(project_id):
    r = _login_required()
    if r: return r
    project = ProjectModel.get(project_id)
    if not project or project["user_id"] != session["user_id"]:
        flash("Project not found.", "error")
        return redirect(url_for("dashboard.index"))
    config   = json.loads(project["config"] or "{}")
    versions = ProjectModel.get_versions(project_id)
    return render_template("editor.html", project=project,
                           config=config, versions=versions, themes=list_themes())


@editor_bp.route("/api/editor/save", methods=["POST"])
def api_save():
    if not session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 401
    data       = request.get_json(silent=True) or {}
    project_id = data.get("project_id")
    config     = data.get("config", {})
    if not project_id or not config:
        return jsonify({"error": "Missing data."}), 400
    project = ProjectModel.get(project_id)
    if not project or project["user_id"] != session["user_id"]:
        return jsonify({"error": "Not found."}), 404
    try:
        ProjectModel.save_version(project_id, project["config"], "auto-save")
        result = AIEngine.generate_from_config(config, project_id)
        ProjectModel.update_config(project_id, session["user_id"],
                                   config.get("site_name", project["name"]),
                                   json.dumps(config))
        ProjectModel.log(session["user_id"], project_id, "editor_save", {})
        return jsonify({"ok": True, "files": result["files"]})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@editor_bp.route("/api/editor/preview", methods=["POST"])
def api_preview():
    if not session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 401
    data   = request.get_json(silent=True) or {}
    config = data.get("config", {})
    if not config:
        return jsonify({"error": "No config."}), 400
    try:
        html = AIEngine.preview_html(config)
        return jsonify({"html": html})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@editor_bp.route("/preview/<project_id>")
def preview(project_id):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    project = ProjectModel.get(project_id)
    if not project or project["user_id"] != session["user_id"]:
        flash("Project not found.", "error")
        return redirect(url_for("dashboard.index"))
    if project["project_type"] == "static":
        html = AIEngine.inline_preview(project_id)
        if html:
            return html
    return render_template("preview.html", project=project)
