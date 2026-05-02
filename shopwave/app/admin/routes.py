import os, uuid
from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app import db
from app.models import (User, Product, Order, OrderItem, SellerEarnings,
                        PlatformEarnings, Coupon, WithdrawalRequest, Review, SellerProfile,
                        Banner, Newsletter, Return, SupportTicket, Notification)
from app.services.payment import record_status_change
from app.services import return_service

admin_bp = Blueprint('admin', __name__)
STATUSES = ['pending', 'paid', 'confirmed', 'shipped', 'delivered', 'cancelled']

def admin_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*a, **kw)
    return dec

def _allowed(fn):
    return '.' in fn and fn.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def _save_img(file):
    if file and file.filename and _allowed(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        fn  = uuid.uuid4().hex + '.' + ext
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fn))
        return fn
    return None

# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_revenue   = db.session.query(db.func.sum(Order.total_price)).scalar() or 0
    platform_income = db.session.query(db.func.sum(PlatformEarnings.amount)).scalar() or 0
    seller_payouts  = db.session.query(db.func.sum(SellerEarnings.amount)).scalar() or 0
    pending_kyc     = User.query.filter_by(kyc_status='pending').count()

    stats = dict(
        users=User.query.count(), sellers=User.query.filter_by(role='seller').count(),
        customers=User.query.filter_by(role='customer').count(),
        products=Product.query.count(), orders=Order.query.count(),
        total_revenue=total_revenue, platform_income=platform_income,
        seller_payouts=seller_payouts,
        pending_orders=Order.query.filter_by(status='pending').count(),
        pending_withdrawals=WithdrawalRequest.query.filter_by(status='pending').count(),
        pending_kyc=pending_kyc,
    )
    recent = Order.query.order_by(Order.created_at.desc()).limit(8).all()

    # Revenue last 7 days for sparkline
    daily_revenue = []
    for i in range(6, -1, -1):
        day   = datetime.utcnow().date() - timedelta(days=i)
        start = datetime.combine(day, datetime.min.time())
        end   = datetime.combine(day, datetime.max.time())
        rev   = db.session.query(db.func.sum(Order.total_price))\
                          .filter(Order.created_at.between(start, end)).scalar() or 0
        daily_revenue.append({'day': day.strftime('%a'), 'revenue': round(rev, 2)})

    top_products = (
        db.session.query(Product.name, db.func.sum(OrderItem.quantity).label('units'))
        .join(OrderItem, Product.id == OrderItem.product_id)
        .group_by(Product.id).order_by(db.text('units DESC')).limit(5).all()
    )
    top_sellers = (
        db.session.query(User.name, db.func.sum(SellerEarnings.amount).label('earned'))
        .join(SellerEarnings, User.id == SellerEarnings.seller_id)
        .group_by(User.id).order_by(db.text('earned DESC')).limit(5).all()
    )

    return render_template('admin/dashboard.html',
                           stats=stats, recent=recent,
                           daily_revenue=daily_revenue,
                           top_products=top_products,
                           top_sellers=top_sellers)

# ── Users ─────────────────────────────────────────────────────────────────────

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    role_filter = request.args.get('role', '')
    q = User.query
    if role_filter:
        q = q.filter_by(role=role_filter)
    users = q.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users, role_filter=role_filter)


@admin_bp.route('/sellers')
@login_required
@admin_required
def sellers():
    sellers = (db.session.query(User, SellerProfile)
               .outerjoin(SellerProfile, User.id == SellerProfile.user_id)
               .filter(User.role == 'seller')
               .order_by(User.created_at.desc()).all())
    return render_template('admin/sellers.html', sellers=sellers)


@admin_bp.route('/users/<int:uid>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(uid):
    u = User.query.get_or_404(uid)
    if u.role == 'admin':
        flash('Cannot delete admin.', 'danger')
        return redirect(url_for('admin.users'))
    db.session.delete(u)
    db.session.commit()
    flash('User deleted.', 'info')
    return redirect(url_for('admin.users'))

# ── Products ──────────────────────────────────────────────────────────────────

@admin_bp.route('/products')
@login_required
@admin_required
def products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products)


@admin_bp.route('/products/<int:pid>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(pid):
    db.session.delete(Product.query.get_or_404(pid))
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('admin.products'))

# ── Orders ────────────────────────────────────────────────────────────────────

@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    status_filter = request.args.get('status', '')
    q = Order.query
    if status_filter:
        q = q.filter_by(status=status_filter)
    orders = q.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders,
                           statuses=STATUSES, status_filter=status_filter)


@admin_bp.route('/orders/<int:oid>/status', methods=['POST'])
@login_required
@admin_required
def update_status(oid):
    order = Order.query.get_or_404(oid)
    new   = request.form.get('status', order.status)
    if new in STATUSES:
        record_status_change(order, new,
                             note=f'Admin updated to {new}',
                             actor_id=current_user.id)
        flash(f'Order #{oid} → {new}', 'success')
    return redirect(url_for('admin.orders'))

# ── Platform Earnings ─────────────────────────────────────────────────────────

@admin_bp.route('/earnings')
@login_required
@admin_required
def earnings():
    rows  = PlatformEarnings.query.order_by(PlatformEarnings.created_at.desc()).all()
    total = sum(r.amount for r in rows)
    seller_summary = (
        db.session.query(User.name, User.email,
                         db.func.sum(SellerEarnings.amount).label('total'))
        .join(SellerEarnings, User.id == SellerEarnings.seller_id)
        .group_by(User.id).order_by(db.text('total DESC')).all()
    )
    monthly: dict = {}
    for r in rows:
        key = r.created_at.strftime('%b %Y')
        monthly[key] = round(monthly.get(key, 0) + r.amount, 2)
    return render_template('admin/earnings.html',
                           rows=rows, total=total,
                           seller_summary=seller_summary, monthly=monthly)

# ── Coupons ───────────────────────────────────────────────────────────────────

@admin_bp.route('/coupons')
@login_required
@admin_required
def coupons():
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    return render_template('admin/coupons.html', coupons=coupons)


@admin_bp.route('/coupons/add', methods=['POST'])
@login_required
@admin_required
def add_coupon():
    expires_raw = request.form.get('expires_at', '').strip()
    expires_at  = datetime.strptime(expires_raw, '%Y-%m-%d') if expires_raw else None
    db.session.add(Coupon(
        code           = request.form['code'].strip().upper(),
        discount_type  = request.form.get('discount_type', 'percent'),
        discount_value = float(request.form['discount_value']),
        min_order      = float(request.form.get('min_order', 0)),
        max_uses       = int(request.form.get('max_uses', 0)),
        expires_at     = expires_at,
    ))
    db.session.commit()
    flash('Coupon created!', 'success')
    return redirect(url_for('admin.coupons'))


@admin_bp.route('/coupons/<int:cid>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_coupon(cid):
    c = Coupon.query.get_or_404(cid)
    c.is_active = not c.is_active
    db.session.commit()
    flash(f'Coupon {"activated" if c.is_active else "deactivated"}.', 'info')
    return redirect(url_for('admin.coupons'))


@admin_bp.route('/coupons/<int:cid>/delete', methods=['POST'])
@login_required
@admin_required
def delete_coupon(cid):
    db.session.delete(Coupon.query.get_or_404(cid))
    db.session.commit()
    flash('Coupon deleted.', 'info')
    return redirect(url_for('admin.coupons'))

# ── Withdrawal Requests ───────────────────────────────────────────────────────

@admin_bp.route('/withdrawals')
@login_required
@admin_required
def withdrawals():
    reqs = WithdrawalRequest.query.order_by(WithdrawalRequest.created_at.desc()).all()
    return render_template('admin/withdrawals.html', reqs=reqs)


@admin_bp.route('/withdrawals/<int:rid>/action', methods=['POST'])
@login_required
@admin_required
def withdrawal_action(rid):
    req    = WithdrawalRequest.query.get_or_404(rid)
    action = request.form.get('action')
    note   = request.form.get('note', '').strip()
    if action in ('approved', 'rejected'):
        req.status = action
        req.note   = note
        db.session.commit()
        flash(f'Withdrawal {action}.', 'success')
    return redirect(url_for('admin.withdrawals'))

# ── Reviews ───────────────────────────────────────────────────────────────────

@admin_bp.route('/reviews')
@login_required
@admin_required
def reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews)


@admin_bp.route('/reviews/<int:rid>/delete', methods=['POST'])
@login_required
@admin_required
def delete_review(rid):
    db.session.delete(Review.query.get_or_404(rid))
    db.session.commit()
    flash('Review deleted.', 'info')
    return redirect(url_for('admin.reviews'))

# ── KYC Queue ─────────────────────────────────────────────────────────────────

@admin_bp.route('/kyc')
@login_required
@admin_required
def kyc_queue():
    pending_sellers = (User.query.filter_by(kyc_status='pending', role='seller')
                       .order_by(User.created_at.desc()).all())
    return render_template('admin/kyc.html', sellers=pending_sellers)


@admin_bp.route('/kyc/<int:uid>/action', methods=['POST'])
@login_required
@admin_required
def kyc_action(uid):
    user   = User.query.get_or_404(uid)
    action = request.form.get('action')  # 'approve' or 'reject'
    note   = request.form.get('note', '').strip()
    if action == 'approve':
        user.kyc_status = 'approved'
        msg = 'Your KYC has been approved! You can now publish products.'
    elif action == 'reject':
        user.kyc_status = 'rejected'
        msg = f'Your KYC was rejected. Reason: {note or "Please resubmit with valid documents."}'
    else:
        flash('Invalid action.', 'danger')
        return redirect(url_for('admin.kyc_queue'))
    db.session.add(Notification(user_id=user.id, message=msg, link='/seller/profile'))
    db.session.commit()
    flash(f'KYC {action}d for {user.name}.', 'success')
    return redirect(url_for('admin.kyc_queue'))

# ── Disputes ──────────────────────────────────────────────────────────────────

@admin_bp.route('/disputes')
@login_required
@admin_required
def disputes():
    returns = Return.query.order_by(Return.created_at.desc()).all()
    return render_template('admin/disputes.html', returns=returns)


@admin_bp.route('/disputes/<int:rid>/action', methods=['POST'])
@login_required
@admin_required
def dispute_action(rid):
    action        = request.form.get('action', 'reject')
    refund_amount = float(request.form.get('refund_amount', 0) or 0)
    admin_note    = request.form.get('admin_note', '').strip()
    try:
        return_service.process_return(rid, action, refund_amount, admin_note, current_user.id)
        flash(f'Return #{rid} has been {action}d.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('admin.disputes'))

# ── Banners ───────────────────────────────────────────────────────────────────

@admin_bp.route('/banners')
@login_required
@admin_required
def banners():
    banner_list = Banner.query.order_by(Banner.position, Banner.created_at.desc()).all()
    return render_template('admin/banners.html', banners=banner_list)


@admin_bp.route('/banners/add', methods=['POST'])
@login_required
@admin_required
def add_banner():
    title    = request.form.get('title', '').strip()
    link     = request.form.get('link', '').strip()
    position = int(request.form.get('position', 0) or 0)
    img_file = request.files.get('image')

    if not title:
        flash('Banner title is required.', 'danger')
        return redirect(url_for('admin.banners'))

    if not img_file or not img_file.filename:
        flash('Banner image is required.', 'danger')
        return redirect(url_for('admin.banners'))

    # Validate image size (max 2MB)
    img_file.seek(0, 2)
    size = img_file.tell()
    img_file.seek(0)
    if size > 2 * 1024 * 1024:
        flash('Banner image must be under 2MB.', 'danger')
        return redirect(url_for('admin.banners'))

    fn = _save_img(img_file)
    if not fn:
        flash('Invalid image format. Use JPEG, PNG, or WebP.', 'danger')
        return redirect(url_for('admin.banners'))

    # Enforce max 3 active banners
    active_count = Banner.query.filter_by(is_active=True).count()
    if active_count >= 3:
        # Deactivate the lowest-position (highest position number) active banner
        oldest = (Banner.query.filter_by(is_active=True)
                  .order_by(Banner.position.desc()).first())
        if oldest:
            oldest.is_active = False

    db.session.add(Banner(title=title, image=fn, link=link, position=position, is_active=True))
    db.session.commit()
    flash('Banner added!', 'success')
    return redirect(url_for('admin.banners'))


@admin_bp.route('/banners/<int:bid>/delete', methods=['POST'])
@login_required
@admin_required
def delete_banner(bid):
    banner = Banner.query.get_or_404(bid)
    db.session.delete(banner)
    db.session.commit()
    flash('Banner deleted.', 'info')
    return redirect(url_for('admin.banners'))


@admin_bp.route('/banners/<int:bid>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_banner(bid):
    banner = Banner.query.get_or_404(bid)
    if not banner.is_active:
        # Activating — check limit
        active_count = Banner.query.filter_by(is_active=True).count()
        if active_count >= 3:
            flash('Maximum 3 active banners allowed. Deactivate one first.', 'warning')
            return redirect(url_for('admin.banners'))
    banner.is_active = not banner.is_active
    db.session.commit()
    flash(f'Banner {"activated" if banner.is_active else "deactivated"}.', 'info')
    return redirect(url_for('admin.banners'))

# ── Newsletter ────────────────────────────────────────────────────────────────

@admin_bp.route('/newsletter')
@login_required
@admin_required
def newsletter():
    subscribers = Newsletter.query.order_by(Newsletter.subscribed_at.desc()).all()
    return render_template('admin/newsletter.html', subscribers=subscribers)


@admin_bp.route('/newsletter/<int:nid>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_newsletter(nid):
    sub = Newsletter.query.get_or_404(nid)
    sub.is_active = not sub.is_active
    db.session.commit()
    flash(f'Subscriber {"reactivated" if sub.is_active else "deactivated"}.', 'info')
    return redirect(url_for('admin.newsletter'))
