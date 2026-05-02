from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import User, Product, Order, SellerProfile, ORDER_STATUSES

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated

# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    stats = {
        'users':     User.query.count(),
        'sellers':   User.query.filter_by(role='seller').count(),
        'customers': User.query.filter_by(role='customer').count(),
        'products':  Product.query.count(),
        'orders':    Order.query.count(),
        'revenue':   db.session.query(db.func.sum(Order.total))
                        .filter(Order.payment_status == 'paid').scalar() or 0,
        'pending':   Order.query.filter_by(status='pending').count(),
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    top_sellers   = (db.session.query(User, SellerProfile)
                     .join(SellerProfile, User.id == SellerProfile.user_id)
                     .order_by(SellerProfile.earnings.desc()).limit(5).all())
    return render_template('admin/dashboard.html',
                           stats=stats, recent_orders=recent_orders, top_sellers=top_sellers)

# ── Users ─────────────────────────────────────────────────────────────────────

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    role   = request.args.get('role', '')
    query  = User.query
    if role:
        query = query.filter_by(role=role)
    users  = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users, role_filter=role)

@admin_bp.route('/users/<int:uid>/toggle-role', methods=['POST'])
@login_required
@admin_required
def toggle_role(uid):
    user = User.query.get_or_404(uid)
    if user.role == 'admin':
        flash('Cannot change admin role.', 'danger')
        return redirect(url_for('admin.users'))
    user.role = 'seller' if user.role == 'customer' else 'customer'
    db.session.commit()
    flash(f'{user.username} is now a {user.role}.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:uid>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(uid):
    user = User.query.get_or_404(uid)
    if user.role == 'admin':
        flash('Cannot delete admin.', 'danger')
        return redirect(url_for('admin.users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'info')
    return redirect(url_for('admin.users'))

# ── Sellers ───────────────────────────────────────────────────────────────────

@admin_bp.route('/sellers')
@login_required
@admin_required
def sellers():
    sellers = (db.session.query(User, SellerProfile)
               .outerjoin(SellerProfile, User.id == SellerProfile.user_id)
               .filter(User.role == 'seller')
               .order_by(User.created_at.desc()).all())
    return render_template('admin/sellers.html', sellers=sellers)

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
    product = Product.query.get_or_404(pid)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('admin.products'))

# ── Orders ────────────────────────────────────────────────────────────────────

@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    status = request.args.get('status', '')
    query  = Order.query
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders,
                           statuses=ORDER_STATUSES, status_filter=status)

@admin_bp.route('/orders/<int:oid>/status', methods=['POST'])
@login_required
@admin_required
def update_order_status(oid):
    order = Order.query.get_or_404(oid)
    new   = request.form.get('status')
    if new in ORDER_STATUSES:
        order.status = new
        db.session.commit()
        flash(f'Order #{oid} → {new}', 'success')
    return redirect(url_for('admin.orders'))
