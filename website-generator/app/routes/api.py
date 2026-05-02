"""
app/routes/api.py — REST API Blueprint
All JSON endpoints for the platform.
"""
import uuid
import json
from flask import Blueprint, request, jsonify, session
from app.models.project import ProjectModel
from app.services.ai_engine import AIEngine, list_themes, get_theme
from codegen import generate_structured

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _auth():
    if not session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 401
    return None


# ── Generate from wizard config ───────────────────────────────────────────────

@api_bp.route("/generate", methods=["POST"])
def generate():
    r = _auth()
    if r: return r
    data   = request.get_json(silent=True) or {}
    config = data.get("config") or session.get("wiz_config", {})
    if not config:
        return jsonify({"error": "No configuration provided."}), 400
    project_id = str(uuid.uuid4())[:8]
    try:
        result = AIEngine.generate_from_config(config, project_id)
        ProjectModel.save(
            project_id   = project_id,
            user_id      = session["user_id"],
            name         = config.get("site_name", "My Project"),
            website_type = config.get("website_type", "business"),
            prompt       = config.get("prompt") or config.get("tagline", ""),
            config       = json.dumps(config),
            project_type = result["type"],
        )
        ProjectModel.log(session["user_id"], project_id, "generate",
                         {"type": result["type"]})
        return jsonify({"project_id": project_id,
                        "files": result["files"], "type": result["type"]})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ── Generate from natural language prompt ─────────────────────────────────────

@api_bp.route("/prompt-generate", methods=["POST"])
def prompt_generate():
    r = _auth()
    if r: return r
    data   = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400
    project_id = str(uuid.uuid4())[:8]
    try:
        from nlp import parse_prompt
        config = parse_prompt(prompt)
        result = AIEngine.generate_from_config(config, project_id)
        ProjectModel.save(
            project_id   = project_id,
            user_id      = session["user_id"],
            name         = config.get("site_name", "My Project"),
            website_type = config.get("website_type", "business"),
            prompt       = prompt,
            config       = json.dumps(config),
            project_type = result["type"],
        )
        ProjectModel.log(session["user_id"], project_id, "prompt_generate",
                         {"prompt": prompt[:100]})
        return jsonify({"project_id": project_id, "files": result["files"],
                        "type": result["type"], "config": config})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ── Structured generation (full output) ──────────────────────────────────────

@api_bp.route("/generate-structured", methods=["POST"])
def generate_structured_api():
    r = _auth()
    if r: return r
    data   = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400
    project_id = str(uuid.uuid4())[:8]
    try:
        result = generate_structured(prompt, project_id)
        ProjectModel.save(
            project_id   = project_id,
            user_id      = session["user_id"],
            name         = result["site_name"],
            website_type = result["website_type"],
            prompt       = prompt,
            config       = json.dumps(result["config"]),
            project_type = result["type"],
        )
        ProjectModel.log(session["user_id"], project_id, "api_codegen",
                         {"prompt": prompt[:100]})
        return jsonify({
            "ok": True,
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


# ── Themes ────────────────────────────────────────────────────────────────────

@api_bp.route("/themes")
def themes():
    return jsonify(list_themes())


@api_bp.route("/theme/<name>")
def theme(name):
    return jsonify(get_theme(name))


# ── Health check ──────────────────────────────────────────────────────────────

@api_bp.route("/health")
def health():
    return jsonify({"status": "ok", "service": "WebGen SaaS Platform"})
