import os, uuid
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from app import db
from app.models import Product, Order, OrderItem, SellerProfile, ORDER_STATUSES

seller_bp = Blueprint('seller', __name__)

CATEGORIES = ['Fashion', 'Electronics', 'Home & Kitchen', 'Beauty', 'Sports', 'Books', 'Toys', 'General']

# ── Helpers ───────────────────────────────────────────────────────────────────

def seller_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ('seller', 'admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file):
    if file and file.filename and allowed_file(file.filename):
        ext  = file.filename.rsplit('.', 1)[1].lower()
        fname = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fname))
        return fname
    return None

def get_or_create_profile(user_id):
    profile = SellerProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = SellerProfile(user_id=user_id, shop_name=current_user.username)
        db.session.add(profile)
        db.session.commit()
    return profile

# ── Dashboard ─────────────────────────────────────────────────────────────────

@seller_bp.route('/dashboard')
@login_required
@seller_required
def dashboard():
    profile  = get_or_create_profile(current_user.id)
    products = Product.query.filter_by(seller_id=current_user.id).order_by(Product.created_at.desc()).all()

    # Earnings & order stats
    seller_pids   = [p.id for p in products]
    items         = OrderItem.query.filter(OrderItem.product_id.in_(seller_pids)).all() if seller_pids else []
    order_ids     = list({i.order_id for i in items})
    total_orders  = len(order_ids)
    pending_count = Order.query.filter(Order.id.in_(order_ids), Order.status == 'pending').count() if order_ids else 0

    return render_template('seller/dashboard.html',
                           products=products, profile=profile,
                           total_orders=total_orders, pending_count=pending_count,
                           categories=CATEGORIES)

# ── Profile ───────────────────────────────────────────────────────────────────

@seller_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@seller_required
def profile():
    p = get_or_create_profile(current_user.id)
    if request.method == 'POST':
        p.shop_name   = request.form.get('shop_name', '').strip() or current_user.username
        p.description = request.form.get('description', '').strip()
        logo = request.files.get('shop_logo')
        saved = save_image(logo)
        if saved:
            p.shop_logo = saved
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('seller.profile'))
    return render_template('seller/profile.html', profile=p)

# ── Products ──────────────────────────────────────────────────────────────────

@seller_bp.route('/product/add', methods=['GET', 'POST'])
@login_required
@seller_required
def add_product():
    if request.method == 'POST':
        img = save_image(request.files.get('image')) or 'default.png'
        product = Product(
            name=request.form['name'].strip(),
            description=request.form.get('description', '').strip(),
            price=float(request.form['price']),
            stock=int(request.form['stock']),
            category=request.form.get('category', 'General'),
            image=img,
            seller_id=current_user.id
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added!', 'success')
        return redirect(url_for('seller.dashboard'))
    return render_template('seller/product_form.html', product=None, categories=CATEGORIES)

@seller_bp.route('/product/<int:pid>/edit', methods=['GET', 'POST'])
@login_required
@seller_required
def edit_product(pid):
    product = Product.query.get_or_404(pid)
    if product.seller_id != current_user.id and current_user.role != 'admin':
        abort(403)
    if request.method == 'POST':
        product.name        = request.form['name'].strip()
        product.description = request.form.get('description', '').strip()
        product.price       = float(request.form['price'])
        product.stock       = int(request.form['stock'])
        product.category    = request.form.get('category', 'General')
        saved = save_image(request.files.get('image'))
        if saved:
            product.image = saved
        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('seller.dashboard'))
    return render_template('seller/product_form.html', product=product, categories=CATEGORIES)

@seller_bp.route('/product/<int:pid>/delete', methods=['POST'])
@login_required
@seller_required
def delete_product(pid):
    product = Product.query.get_or_404(pid)
    if product.seller_id != current_user.id and current_user.role != 'admin':
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('seller.dashboard'))

# ── Orders ────────────────────────────────────────────────────────────────────

@seller_bp.route('/orders')
@login_required
@seller_required
def orders():
    seller_pids = [p.id for p in Product.query.filter_by(seller_id=current_user.id).all()]
    items       = OrderItem.query.filter(OrderItem.product_id.in_(seller_pids)).all() if seller_pids else []
    order_ids   = list({i.order_id for i in items})
    seller_orders = Order.query.filter(Order.id.in_(order_ids)).order_by(Order.created_at.desc()).all() if order_ids else []
    return render_template('seller/orders.html',
                           orders=seller_orders,
                           seller_product_ids=seller_pids,
                           statuses=ORDER_STATUSES)

@seller_bp.route('/orders/<int:oid>/status', methods=['POST'])
@login_required
@seller_required
def update_order_status(oid):
    order = Order.query.get_or_404(oid)
    # Verify this seller owns at least one item in the order
    seller_pids = [p.id for p in Product.query.filter_by(seller_id=current_user.id).all()]
    if not any(i.product_id in seller_pids for i in order.items):
        abort(403)
    new_status = request.form.get('status')
    if new_status in ORDER_STATUSES:
        old_status = order.status
        order.status = new_status
        # Credit earnings when delivered
        if new_status == 'delivered' and old_status != 'delivered':
            profile = get_or_create_profile(current_user.id)
            seller_total = sum(
                i.price * i.quantity for i in order.items if i.product_id in seller_pids
            )
            profile.earnings += seller_total
        db.session.commit()
        flash(f'Order #{oid} status → {new_status}', 'success')
    return redirect(url_for('seller.orders'))

# ── Earnings ──────────────────────────────────────────────────────────────────

@seller_bp.route('/earnings')
@login_required
@seller_required
def earnings():
    profile     = get_or_create_profile(current_user.id)
    seller_pids = [p.id for p in Product.query.filter_by(seller_id=current_user.id).all()]
    items       = OrderItem.query.filter(OrderItem.product_id.in_(seller_pids)).all() if seller_pids else []
    order_ids   = list({i.order_id for i in items})
    delivered   = Order.query.filter(Order.id.in_(order_ids), Order.status == 'delivered').all() if order_ids else []
    monthly     = {}
    for o in delivered:
        key = o.created_at.strftime('%b %Y')
        seller_amt = sum(i.price * i.quantity for i in o.items if i.product_id in seller_pids)
        monthly[key] = monthly.get(key, 0) + seller_amt
    return render_template('seller/earnings.html', profile=profile, monthly=monthly, delivered=delivered,
                           seller_pids=seller_pids)
