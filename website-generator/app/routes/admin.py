"""
app/routes/admin.py — Admin Panel Blueprint
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session)
from app.models.user import UserModel
import db as database

admin_bp = Blueprint("admin", __name__)


def _admin_required():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    user = UserModel.get_by_id(session["user_id"])
    if not user or not user["is_admin"]:
        flash("Admin access required.", "error")
        return redirect(url_for("dashboard.index"))
    return None


@admin_bp.route("/admin")
def index():
    r = _admin_required()
    if r: return r
    stats = database.get_platform_stats()
    users = UserModel.get_all()
    return render_template("admin/index.html", stats=stats, users=users)


@admin_bp.route("/admin/user/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    r = _admin_required()
    if r: return r
    if user_id == session["user_id"]:
        flash("Cannot delete your own account.", "error")
    else:
        UserModel.delete(user_id)
        flash("User deleted.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/admin/make-admin/<int:user_id>", methods=["POST"])
def make_admin(user_id):
    r = _admin_required()
    if r: return r
    UserModel.make_admin(user_id)
    flash("User promoted to admin.", "success")
    return redirect(url_for("admin.index"))
