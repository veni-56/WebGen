"""
app/routes/auth.py — Authentication Blueprint
Handles: signup, login, logout, account settings
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session)
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import UserModel

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = UserModel.get_by_username(username)
        if user and check_password_hash(user["password"], password):
            session["user_id"]  = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = bool(user["is_admin"])
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("dashboard.index"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        username = request.form["username"].strip()
        email    = request.form["email"].strip()
        pwd      = request.form["password"]
        if len(pwd) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("signup.html")
        if UserModel.create(username, email, generate_password_hash(pwd)):
            flash("Account created! Please login.", "success")
            return redirect(url_for("auth.login"))
        flash("Username or email already exists.", "error")
    return render_template("signup.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@auth_bp.route("/account", methods=["GET", "POST"])
def account():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        current = request.form.get("current_password", "")
        new_pwd = request.form.get("new_password", "")
        user = UserModel.get_by_id(session["user_id"])
        if not check_password_hash(user["password"], current):
            flash("Current password is incorrect.", "error")
        elif len(new_pwd) < 6:
            flash("New password must be at least 6 characters.", "error")
        else:
            UserModel.update_password(session["user_id"], generate_password_hash(new_pwd))
            flash("Password updated successfully.", "success")
    user     = UserModel.get_by_id(session["user_id"])
    from app.models.project import ProjectModel
    projects = ProjectModel.get_for_user(session["user_id"])
    return render_template("account.html", user=user, project_count=len(projects))
