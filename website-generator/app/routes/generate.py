"""
app/routes/generate.py — Generation Blueprint
Handles: wizard steps, /generate page, structured output
"""
import uuid
import json
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session)
from app.models.project import ProjectModel
from app.services.ai_engine import AIEngine, list_themes
from codegen import generate_structured

generate_bp = Blueprint("generate", __name__)


def _login_required():
    if not session.get("user_id"):
        flash("Please login to continue.", "error")
        return redirect(url_for("auth.login"))
    return None


# ── Wizard ────────────────────────────────────────────────────────────────────

@generate_bp.route("/wizard/step1")
def wizard_step1():
    r = _login_required()
    if r: return r
    return render_template("wizard/step1.html")


@generate_bp.route("/wizard/step2", methods=["GET", "POST"])
def wizard_step2():
    r = _login_required()
    if r: return r
    if request.method == "POST":
        session["wiz_type"]  = request.form.get("website_type", "business")
        session["wiz_stack"] = request.form.get("stack", "static")
    return render_template("wizard/step2.html",
                           wiz_type=session.get("wiz_type", "business"),
                           wiz_stack=session.get("wiz_stack", "static"),
                           themes=list_themes())


@generate_bp.route("/wizard/step3", methods=["GET", "POST"])
def wizard_step3():
    r = _login_required()
    if r: return r
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
            "project_type":    _resolve_type(stack, wtype),
        }
    config = session.get("wiz_config", {})
    return render_template("wizard/step3.html", config=config)


def _resolve_type(stack: str, wtype: str) -> str:
    if wtype == "ecommerce": return "ecommerce"
    if stack in ("flask", "fullstack"): return "flask"
    if any(k in wtype for k in ["startup", "saas"]): return "startup"
    return "static"


# ── /generate — structured output page ───────────────────────────────────────

@generate_bp.route("/generate", methods=["GET", "POST"])
def generate_page():
    r = _login_required()
    if r: return r
    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if not prompt:
            flash("Please enter a prompt.", "error")
            return render_template("generate.html", themes=list_themes())
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
            ProjectModel.log(session["user_id"], project_id, "codegen",
                             {"prompt": prompt[:100]})
            return render_template("generate_output.html", result=result, prompt=prompt)
        except Exception as exc:
            flash(f"Generation failed: {exc}", "error")
    return render_template("generate.html", themes=list_themes())


# ── Pricing page ──────────────────────────────────────────────────────────────
from flask import render_template as _rt
from billing import PLANS, get_user_plan

@generate_bp.route("/pricing")
def pricing():
    user_plan = get_user_plan(session.get("user_id")) if session.get("user_id") else "free"
    return _rt("pricing.html", plans=PLANS, user_plan=user_plan)

@generate_bp.route("/billing/checkout/<plan>", methods=["POST"])
def billing_checkout(plan):
    from flask import flash, redirect, url_for, session
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    # Mock upgrade — works without Stripe keys
    import db as database
    database.update_user_plan(session["user_id"], plan)
    flash(f"Upgraded to {plan.title()} plan!", "success")
    return redirect(url_for("auth.account"))


# ── Chat Builder ──────────────────────────────────────────────────────────────
from flask import session as _session, render_template as _rt2, request as _req2, jsonify as _json2

@generate_bp.route("/chat")
def chat_builder():
    if not _session.get("user_id"):
        from flask import redirect, url_for
        return redirect(url_for("auth.login"))
    return _rt2("chat.html")


@generate_bp.route("/api/chat", methods=["POST"])
def chat_api():
    if not _session.get("user_id"):
        return _json2({"error": "Login required"}), 401
    data    = _req2.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return _json2({"error": "Message required"}), 400
    try:
        from app.services.ai_engine import parse_prompt, list_themes
        parsed = parse_prompt(message)
        return _json2({
            "ok":      True,
            "parsed":  parsed,
            "message": f"I'll build a {parsed.get('project_type','website')} for you! Redirecting to generator...",
            "redirect": "/generate"
        })
    except Exception as e:
        return _json2({"ok": True, "message": f"Great idea! Let me generate that for you.", "redirect": "/generate"})
