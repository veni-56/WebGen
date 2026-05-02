import re
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, SellerProfile
from app.services import otp_service, referral_service

auth_bp = Blueprint('auth', __name__)


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text or 'shop'


# ── Signup ────────────────────────────────────────────────────────────────────

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('customer.home'))
    if request.method == 'POST':
        name      = request.form['name'].strip()
        email     = request.form['email'].strip().lower()
        password  = request.form['password']
        role      = request.form.get('role', 'customer')
        shop_name = request.form.get('shop_name', '').strip()
        ref_code  = request.args.get('ref', '').strip()

        if role not in ('seller', 'customer'):
            role = 'customer'
        if role == 'seller' and not shop_name:
            flash('Please enter your shop name.', 'danger')
            return redirect(url_for('auth.signup'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.signup'))
        if role == 'seller':
            slug = _slugify(shop_name)
            if SellerProfile.query.filter_by(shop_slug=slug).first():
                flash('That shop name is already taken.', 'danger')
                return redirect(url_for('auth.signup'))

        user = User(name=name, email=email,
                    password=generate_password_hash(password), role=role)
        db.session.add(user)
        db.session.flush()

        if role == 'seller':
            slug = _slugify(shop_name)
            db.session.add(SellerProfile(user_id=user.id, shop_name=shop_name, shop_slug=slug))

        db.session.commit()

        # Generate referral code for every new user
        referral_service.generate_referral_code(user.id)

        # Apply referral if code present
        if ref_code:
            referral_service.apply_referral(user, ref_code)

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/signup.html')


# ── Login ─────────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('customer.home'))
    if request.method == 'POST':
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            if not user.is_active:
                flash('Your account has been deactivated. Contact support.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            if user.role == 'seller':
                return redirect(url_for('seller.dashboard'))
            return redirect(url_for('customer.home'))
        flash('Invalid credentials.', 'danger')
    return render_template('auth/login.html')


# ── OTP Login ─────────────────────────────────────────────────────────────────

@auth_bp.route('/accounts/otp/request/', methods=['GET', 'POST'])
def otp_request():
    if current_user.is_authenticated:
        return redirect(url_for('customer.home'))
    if request.method == 'POST':
        mobile = request.form.get('mobile', '').strip()
        if not mobile or not re.fullmatch(r'\d{10}', mobile):
            flash('Please enter a valid 10-digit mobile number.', 'danger')
            return redirect(url_for('auth.otp_request'))
        if not otp_service.can_request_otp(mobile):
            flash('Too many OTP requests. Please try again after 1 hour.', 'danger')
            return redirect(url_for('auth.otp_request'))
        otp_service.generate_otp(mobile)
        from flask import session as flask_session
        flask_session['otp_mobile'] = mobile
        flash(f'OTP sent to {mobile[:4]}****{mobile[-2:]}', 'info')
        return redirect(url_for('auth.otp_verify'))
    return render_template('auth/otp_request.html')


@auth_bp.route('/accounts/otp/verify/', methods=['GET', 'POST'])
def otp_verify():
    from flask import session as flask_session
    mobile = flask_session.get('otp_mobile', '')
    if not mobile:
        return redirect(url_for('auth.otp_request'))
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        if not otp_service.verify_otp(mobile, code):
            flash('Invalid or expired OTP.', 'danger')
            return redirect(url_for('auth.otp_verify'))
        # Find or create user
        user = User.query.filter_by(mobile=mobile).first()
        if not user:
            import secrets
            user = User(
                name=f'User_{mobile[-4:]}',
                email=f'otp_{mobile}@noemail.local',
                password=generate_password_hash(secrets.token_hex(16)),
                role='customer',
                mobile=mobile,
            )
            db.session.add(user)
            db.session.commit()
            referral_service.generate_referral_code(user.id)
        if not user.is_active:
            flash('Your account has been deactivated.', 'danger')
            return redirect(url_for('auth.otp_request'))
        flask_session.pop('otp_mobile', None)
        login_user(user)
        flash('Logged in successfully!', 'success')
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        if user.role == 'seller':
            return redirect(url_for('seller.dashboard'))
        return redirect(url_for('customer.home'))
    return render_template('auth/otp_verify.html', mobile=mobile)


# ── Logout ────────────────────────────────────────────────────────────────────

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))
