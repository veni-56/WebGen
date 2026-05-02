"""
app/routes/dashboard.py — Dashboard Blueprint
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.project import ProjectModel
from app.services.ai_engine import AIEngine, list_themes

dashboard_bp = Blueprint("dashboard", __name__)


def _login_required():
    if not session.get("user_id"):
        flash("Please login to continue.", "error")
        return redirect(url_for("auth.login"))
    return None


@dashboard_bp.route("/dashboard")
def index():
    redir = _login_required()
    if redir:
        return redir
    projects = ProjectModel.get_for_user(session["user_id"])
    return render_template("dashboard.html", projects=projects)


@dashboard_bp.route("/quick-generate", methods=["GET", "POST"])
def quick_generate():
    redir = _login_required()
    if redir:
        return redir
    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if not prompt:
            flash("Please enter a description.", "error")
            return redirect(url_for("dashboard.index"))
        from nlp import parse_prompt
        config = parse_prompt(prompt)
        session["wiz_config"] = config
        session["wiz_type"]   = config["website_type"]
        session["wiz_stack"]  = config["project_type"]
        return redirect(url_for("generate.wizard_step3"))
    return render_template("quick_generate.html", themes=list_themes())
