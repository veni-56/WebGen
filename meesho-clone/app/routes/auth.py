from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('customer.index'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        role     = request.form.get('role', 'customer')
        if role not in ('seller', 'customer'):
            role = 'customer'
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.signup'))
        if User.query.filter_by(username=username).first():
            flash('Username taken.', 'danger')
            return redirect(url_for('auth.signup'))
        user = User(username=username, email=email,
                    password=generate_password_hash(password), role=role)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('customer.index'))
    if request.method == 'POST':
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            if user.role == 'admin':
                return redirect(next_page or url_for('admin.dashboard'))
            if user.role == 'seller':
                return redirect(next_page or url_for('seller.dashboard'))
            return redirect(next_page or url_for('customer.index'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))
