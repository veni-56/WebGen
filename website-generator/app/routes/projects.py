"""
app/routes/projects.py — Project Management Blueprint
Handles: duplicate, rename, delete, versions, download
"""
import json
import uuid
from flask import (Blueprint, request, jsonify, redirect,
                   url_for, flash, session, send_file)
from app.models.project import ProjectModel
from app.services.ai_engine import AIEngine
from app.services.file_service import FileService

projects_bp = Blueprint("projects", __name__)


def _login_required():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    return None


@projects_bp.route("/project/duplicate/<project_id>", methods=["POST"])
def duplicate(project_id):
    r = _login_required()
    if r: return r
    new_id = str(uuid.uuid4())[:8]
    if ProjectModel.duplicate(project_id, session["user_id"], new_id):
        FileService.copy(project_id, new_id)
        flash("Project duplicated.", "success")
    else:
        flash("Could not duplicate project.", "error")
    return redirect(url_for("dashboard.index"))


@projects_bp.route("/project/rename/<project_id>", methods=["POST"])
def rename(project_id):
    if not session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 401
    new_name = request.form.get("name", "").strip()
    if new_name and ProjectModel.rename(project_id, session["user_id"], new_name):
        return jsonify({"ok": True})
    return jsonify({"error": "Could not rename."}), 400


@projects_bp.route("/project/delete/<project_id>", methods=["POST"])
def delete(project_id):
    r = _login_required()
    if r: return r
    ProjectModel.delete(project_id, session["user_id"])
    FileService.delete(project_id)
    flash("Project deleted.", "success")
    return redirect(url_for("dashboard.index"))


@projects_bp.route("/project/versions/<project_id>")
def versions(project_id):
    r = _login_required()
    if r: return r
    from flask import render_template
    project  = ProjectModel.get(project_id)
    if not project or project["user_id"] != session["user_id"]:
        flash("Project not found.", "error")
        return redirect(url_for("dashboard.index"))
    vers = ProjectModel.get_versions(project_id)
    return render_template("versions.html", project=project, versions=vers)


@projects_bp.route("/api/version/restore", methods=["POST"])
def restore_version():
    if not session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 401
    data       = request.get_json(silent=True) or {}
    project_id = data.get("project_id")
    config_str = data.get("config")
    if not project_id or not config_str:
        return jsonify({"error": "Missing data."}), 400
    project = ProjectModel.get(project_id)
    if not project or project["user_id"] != session["user_id"]:
        return jsonify({"error": "Not found."}), 404
    try:
        config = json.loads(config_str)
        AIEngine.generate_from_config(config, project_id)
        ProjectModel.update_config(project_id, session["user_id"],
                                   config.get("site_name", project["name"]),
                                   config_str)
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@projects_bp.route("/download/<project_id>")
def download(project_id):
    r = _login_required()
    if r: return r
    project = ProjectModel.get(project_id)
    if not project or project["user_id"] != session["user_id"]:
        flash("Project not found.", "error")
        return redirect(url_for("dashboard.index"))
    if not FileService.exists(project_id):
        flash("Project files not found. Please regenerate.", "error")
        return redirect(url_for("dashboard.index"))
    zip_path = FileService.zip(project_id)
    ProjectModel.log(session["user_id"], project_id, "download", {})
    return send_file(zip_path, as_attachment=True,
                     download_name=f"{project['name'].replace(' ','_')}.zip")


@projects_bp.route("/file/<project_id>/<path:filepath>")
def view_file(project_id, filepath):
    if not session.get("user_id"):
        return "Unauthorized", 401
    content = FileService.read(project_id, filepath)
    if content is None:
        return "File not found", 404
    return content, 200, {"Content-Type": "text/plain; charset=utf-8"}
