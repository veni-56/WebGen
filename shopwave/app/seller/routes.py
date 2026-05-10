import os, uuid
from functools import wraps
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, current_app, abort)
from flask_login import login_required, current_user
from app import db
from app.models import (Product, Order, OrderItem, SellerEarnings, WithdrawalRequest,
                        Notification, SellerProfile, ProductVariant, Shipping, Return,
                        SupportTicket)
from app.services.payment import record_status_change
from app.services import shipping_service, return_service
from app.utils import unique_product_slug

seller_bp = Blueprint('seller', __name__)
CATEGORIES = ['Fashion', 'Electronics', 'Home & Kitchen', 'Beauty',
              'Sports', 'Books', 'Toys', 'General']
STATUSES   = ['pending', 'paid', 'confirmed', 'shipped', 'delivered', 'cancelled']

# ── Decorators ────────────────────────────────────────────────────────────────

def seller_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if not current_user.is_authenticated or current_user.role not in ('seller', 'admin'):
            abort(403)
        return f(*a, **kw)
    return dec

# ── Image helpers ─────────────────────────────────────────────────────────────

def _allowed(fn):
    return '.' in fn and fn.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def _save_img(file):
    if file and file.filename and _allowed(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        fn  = uuid.uuid4().hex + '.' + ext
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fn))
        return fn
    return 'default.png'

# ── Dashboard ─────────────────────────────────────────────────────────────────

@seller_bp.route('/dashboard')
@login_required
@seller_required
def dashboard():
    profile = SellerProfile.query.filter_by(user_id=current_user.id).first()
    products = (Product.query.filter_by(seller_id=current_user.id)
                .order_by(Product.created_at.desc()).all())
    pids  = [p.id for p in products]
    items = OrderItem.query.filter(OrderItem.product_id.in_(pids)).all() if pids else []
    oids  = list({i.order_id for i in items})
    recent_orders = (Order.query.filter(Order.id.in_(oids))
                     .order_by(Order.created_at.desc()).limit(5).all() if oids else [])
    total_earned = (db.session.query(db.func.sum(SellerEarnings.amount))
                    .filter_by(seller_id=current_user.id).scalar() or 0)
    withdrawn = (db.session.query(db.func.sum(WithdrawalRequest.amount))
                 .filter_by(seller_id=current_user.id, status='approved').scalar() or 0)
    unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return render_template('seller/dashboard.html',
                           products=products, recent_orders=recent_orders,
                           total_earned=total_earned, total_orders=len(oids),
                           total_units=sum(i.quantity for i in items),
                           wallet_balance=round(total_earned - withdrawn, 2),
                           unread=unread, profile=profile)

# ── Products ──────────────────────────────────────────────────────────────────

@seller_bp.route('/product/add', methods=['GET', 'POST'])
@login_required
@seller_required
def add_product():
    if request.method == 'POST':
        name             = request.form['name'].strip()
        discount_percent = float(request.form.get('discount_percent', 0) or 0)
        status           = request.form.get('status', 'draft')

        # Block active status if KYC not approved
        if False and current_user.kyc_status != 'approved':  # KYC check disabled for demo
            status = 'draft'
            flash('Product saved as draft. KYC approval required to publish.', 'warning')

        # Generate slug
        slug = unique_product_slug(name)

        # Primary image
        primary_img = _save_img(request.files.get('image'))

        # Multi-image upload (up to 5)
        image_files = request.files.getlist('images')
        saved_images = []
        for f in image_files[:5]:
            fn = _save_img(f)
            if fn != 'default.png':
                saved_images.append(fn)

        product = Product(
            name             = name,
            description      = request.form.get('description', '').strip(),
            price            = float(request.form['price']),
            stock            = int(request.form.get('stock', 0)),
            category         = request.form.get('category', 'General'),
            image            = primary_img,
            images           = ','.join(saved_images),
            seller_id        = current_user.id,
            slug             = slug,
            discount_percent = min(100.0, max(0.0, discount_percent)),
            status           = status,
        )
        db.session.add(product)
        db.session.flush()

        # Variants
        sizes   = request.form.getlist('variant_size[]')
        colors  = request.form.getlist('variant_color[]')
        prices  = request.form.getlist('variant_price[]')
        stocks  = request.form.getlist('variant_stock[]')
        skus    = request.form.getlist('variant_sku[]')
        for i in range(len(sizes)):
            try:
                vp = float(prices[i]) if i < len(prices) and prices[i] else product.price
                vs = int(stocks[i])   if i < len(stocks) and stocks[i] else 0
            except (ValueError, IndexError):
                continue
            db.session.add(ProductVariant(
                product_id = product.id,
                size       = sizes[i] if i < len(sizes) else '',
                color      = colors[i] if i < len(colors) else '',
                price      = vp,
                stock      = vs,
                sku        = skus[i] if i < len(skus) else '',
            ))

        db.session.commit()
        flash('Product added!', 'success')
        return redirect(url_for('seller.dashboard'))
    return render_template('seller/product_form.html', product=None, categories=CATEGORIES)


@seller_bp.route('/product/<int:pid>/edit', methods=['GET', 'POST'])
@login_required
@seller_required
def edit_product(pid):
    p = Product.query.get_or_404(pid)
    if p.seller_id != current_user.id and current_user.role != 'admin':
        abort(403)
    if request.method == 'POST':
        p.name        = request.form['name'].strip()
        p.description = request.form.get('description', '').strip()
        p.price       = float(request.form['price'])
        p.stock       = int(request.form.get('stock', 0))
        p.category    = request.form.get('category', 'General')
        p.discount_percent = min(100.0, max(0.0, float(request.form.get('discount_percent', 0) or 0)))

        status = request.form.get('status', p.status)
        if False and current_user.kyc_status != 'approved':  # KYC check disabled for demo
            status = 'draft'
            flash('KYC approval required to publish products.', 'warning')
        p.status = status

        # Regenerate slug if name changed
        if not p.slug:
            p.slug = unique_product_slug(p.name, p.id)

        img = request.files.get('image')
        if img and img.filename:
            p.image = _save_img(img)

        # Multi-image
        image_files = request.files.getlist('images')
        saved_images = []
        for f in image_files[:5]:
            fn = _save_img(f)
            if fn != 'default.png':
                saved_images.append(fn)
        if saved_images:
            p.images = ','.join(saved_images)

        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('seller.dashboard'))
    return render_template('seller/product_form.html', product=p, categories=CATEGORIES)


@seller_bp.route('/product/<int:pid>/delete', methods=['POST'])
@login_required
@seller_required
def delete_product(pid):
    p = Product.query.get_or_404(pid)
    if p.seller_id != current_user.id and current_user.role != 'admin':
        abort(403)
    db.session.delete(p)
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('seller.dashboard'))

# ── Inventory ─────────────────────────────────────────────────────────────────

@seller_bp.route('/inventory')
@login_required
@seller_required
def inventory():
    products = (Product.query.filter_by(seller_id=current_user.id)
                .order_by(Product.name).all())
    return render_template('seller/inventory.html', products=products)


@seller_bp.route('/inventory/<int:pid>/update', methods=['POST'])
@login_required
@seller_required
def update_inventory(pid):
    p = Product.query.get_or_404(pid)
    if p.seller_id != current_user.id and current_user.role != 'admin':
        abort(403)

    # Update base stock
    new_stock = request.form.get('stock', type=int)
    if new_stock is not None and new_stock >= 0:
        p.stock = new_stock

    # Update variant stocks
    for key, val in request.form.items():
        if key.startswith('variant_stock_'):
            try:
                vid = int(key.split('_')[-1])
                variant = ProductVariant.query.get(vid)
                if variant and variant.product_id == p.id:
                    variant.stock = max(0, int(val))
            except (ValueError, TypeError):
                pass

    db.session.commit()
    flash(f'Inventory updated for "{p.name}".', 'success')
    return redirect(url_for('seller.inventory'))

# ── Orders ────────────────────────────────────────────────────────────────────

@seller_bp.route('/orders')
@login_required
@seller_required
def orders():
    pids  = [p.id for p in Product.query.filter_by(seller_id=current_user.id).all()]
    items = OrderItem.query.filter(OrderItem.product_id.in_(pids)).all() if pids else []
    oids  = list({i.order_id for i in items})
    seller_orders = (Order.query.filter(Order.id.in_(oids))
                     .order_by(Order.created_at.desc()).all() if oids else [])
    return render_template('seller/orders.html',
                           orders=seller_orders, pids=pids, statuses=STATUSES)


@seller_bp.route('/orders/<int:oid>/status', methods=['POST'])
@login_required
@seller_required
def update_status(oid):
    order = Order.query.get_or_404(oid)
    pids  = [p.id for p in Product.query.filter_by(seller_id=current_user.id).all()]
    if not any(i.product_id in pids for i in order.items):
        abort(403)
    new_status = request.form.get('status', order.status)
    if new_status in STATUSES:
        record_status_change(order, new_status,
                             note=request.form.get('note', ''),
                             actor_id=current_user.id)
        flash(f'Order #{oid} → {new_status}', 'success')
    return redirect(url_for('seller.orders'))

# ── Payments ──────────────────────────────────────────────────────────────────

@seller_bp.route('/payments')
@login_required
@seller_required
def payments():
    rows = (SellerEarnings.query.filter_by(seller_id=current_user.id)
            .order_by(SellerEarnings.created_at.desc()).all())
    total_earned = sum(r.amount for r in rows)
    withdrawn    = (db.session.query(db.func.sum(WithdrawalRequest.amount))
                    .filter_by(seller_id=current_user.id, status='approved').scalar() or 0)
    monthly: dict = {}
    for r in rows:
        key = r.created_at.strftime('%b %Y')
        monthly[key] = round(monthly.get(key, 0) + r.amount, 2)
    withdrawals = (WithdrawalRequest.query.filter_by(seller_id=current_user.id)
                   .order_by(WithdrawalRequest.created_at.desc()).all())
    return render_template('seller/payments.html',
                           rows=rows, total_earned=total_earned,
                           total_orders=len({r.order_id for r in rows}),
                           monthly=monthly,
                           wallet_balance=round(total_earned - withdrawn, 2),
                           withdrawals=withdrawals)

# ── Earnings (alias for payments) ────────────────────────────────────────────

@seller_bp.route('/earnings')
@login_required
@seller_required
def earnings():
    return redirect(url_for('seller.payments'))

# ── Wallet / Withdrawal ───────────────────────────────────────────────────────

@seller_bp.route('/wallet/withdraw', methods=['POST'])
@login_required
@seller_required
def request_withdrawal():
    amount = float(request.form.get('amount', 0))
    upi_id = request.form.get('upi_id', '').strip()
    total_earned = (db.session.query(db.func.sum(SellerEarnings.amount))
                    .filter_by(seller_id=current_user.id).scalar() or 0)
    withdrawn    = (db.session.query(db.func.sum(WithdrawalRequest.amount))
                    .filter_by(seller_id=current_user.id, status='approved').scalar() or 0)
    balance = round(total_earned - withdrawn, 2)
    if amount <= 0 or amount > balance:
        flash(f'Invalid amount. Available balance: ₹{balance:.2f}', 'danger')
        return redirect(url_for('seller.payments'))
    if not upi_id:
        flash('Please enter your UPI ID.', 'danger')
        return redirect(url_for('seller.payments'))
    db.session.add(WithdrawalRequest(
        seller_id=current_user.id, amount=amount, upi_id=upi_id))
    db.session.commit()
    flash(f'Withdrawal request of ₹{amount:.2f} submitted!', 'success')
    return redirect(url_for('seller.payments'))

# ── Shipments ─────────────────────────────────────────────────────────────────

@seller_bp.route('/shipments')
@login_required
@seller_required
def shipments():
    pids  = [p.id for p in Product.query.filter_by(seller_id=current_user.id).all()]
    items = OrderItem.query.filter(OrderItem.product_id.in_(pids)).all() if pids else []
    oids  = list({i.order_id for i in items})
    shipment_list = (Shipping.query.filter(Shipping.order_id.in_(oids))
                     .order_by(Shipping.created_at.desc()).all() if oids else [])
    return render_template('seller/shipments.html', shipments=shipment_list)


@seller_bp.route('/shipments/<int:oid>/update', methods=['POST'])
@login_required
@seller_required
def update_shipment(oid):
    order = Order.query.get_or_404(oid)
    pids  = [p.id for p in Product.query.filter_by(seller_id=current_user.id).all()]
    if not any(i.product_id in pids for i in order.items):
        abort(403)
    carrier          = request.form.get('carrier', '').strip()
    tracking_number  = request.form.get('tracking_number', '').strip()
    status           = request.form.get('status', 'pending')
    estimated_raw    = request.form.get('estimated_delivery', '').strip()
    estimated_delivery = None
    if estimated_raw:
        from datetime import datetime
        try:
            estimated_delivery = datetime.strptime(estimated_raw, '%Y-%m-%d')
        except ValueError:
            pass
    shipping_service.update_tracking(oid, carrier, tracking_number, status, estimated_delivery)
    flash(f'Shipment for order #{oid} updated.', 'success')
    return redirect(url_for('seller.shipments'))

# ── Returns ───────────────────────────────────────────────────────────────────

@seller_bp.route('/returns')
@login_required
@seller_required
def seller_returns():
    pids  = [p.id for p in Product.query.filter_by(seller_id=current_user.id).all()]
    items = OrderItem.query.filter(OrderItem.product_id.in_(pids)).all() if pids else []
    oids  = list({i.order_id for i in items})
    returns = (Return.query.filter(Return.order_id.in_(oids))
               .order_by(Return.created_at.desc()).all() if oids else [])
    return render_template('seller/returns.html', returns=returns)


@seller_bp.route('/returns/<int:rid>/respond', methods=['POST'])
@login_required
@seller_required
def respond_return(rid):
    ret = Return.query.get_or_404(rid)
    # Verify this return belongs to seller's products
    pids = [p.id for p in Product.query.filter_by(seller_id=current_user.id).all()]
    order_items = OrderItem.query.filter_by(order_id=ret.order_id).all()
    if not any(i.product_id in pids for i in order_items):
        abort(403)
    action        = request.form.get('action', 'reject')
    refund_amount = float(request.form.get('refund_amount', ret.refund_amount) or 0)
    admin_note    = request.form.get('note', '').strip()
    try:
        return_service.process_return(rid, action, refund_amount, admin_note, current_user.id)
        flash(f'Return #{rid} has been {action}d.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('seller.seller_returns'))

# ── Support Tickets ───────────────────────────────────────────────────────────

@seller_bp.route('/support')
@login_required
@seller_required
def support_tickets():
    tickets = (SupportTicket.query.filter_by(user_id=current_user.id)
               .order_by(SupportTicket.created_at.desc()).all())
    return render_template('seller/support.html', tickets=tickets)


@seller_bp.route('/support/new', methods=['POST'])
@login_required
@seller_required
def create_ticket():
    subject     = request.form.get('subject', '').strip()
    description = request.form.get('description', '').strip()
    priority    = request.form.get('priority', 'normal')
    if not subject or not description:
        flash('Subject and description are required.', 'danger')
        return redirect(url_for('seller.support_tickets'))
    if priority not in ('low', 'normal', 'high'):
        priority = 'normal'
    db.session.add(SupportTicket(
        user_id=current_user.id,
        subject=subject,
        description=description,
        priority=priority,
    ))
    db.session.commit()
    flash('Support ticket submitted!', 'success')
    return redirect(url_for('seller.support_tickets'))

# ── Notifications ─────────────────────────────────────────────────────────────

@seller_bp.route('/notifications')
@login_required
@seller_required
def notifications():
    notifs = (Notification.query.filter_by(user_id=current_user.id)
              .order_by(Notification.created_at.desc()).all())
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template('seller/notifications.html', notifications=notifs)


# ── Shop Profile ──────────────────────────────────────────────────────────────

@seller_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@seller_required
def shop_profile():
    profile = SellerProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('No shop profile found. Please contact support.', 'danger')
        return redirect(url_for('seller.dashboard'))
    if request.method == 'POST':
        new_name = request.form.get('shop_name', '').strip()
        desc     = request.form.get('description', '').strip()
        logo_f   = request.files.get('logo')
        kyc_doc  = request.files.get('kyc_doc')

        if new_name and new_name != profile.shop_name:
            import re
            slug = re.sub(r'[\s_-]+', '-', re.sub(r'[^\w\s-]', '', new_name.lower().strip()))
            existing = SellerProfile.query.filter_by(shop_slug=slug).first()
            if existing and existing.id != profile.id:
                flash('That shop name is already taken.', 'danger')
                return redirect(url_for('seller.shop_profile'))
            profile.shop_name = new_name
            profile.shop_slug = slug
        profile.description = desc
        if logo_f and logo_f.filename:
            profile.logo = _save_img(logo_f)

        # KYC document upload
        if kyc_doc and kyc_doc.filename:
            if kyc_doc.content_length and kyc_doc.content_length > 5 * 1024 * 1024:
                flash('KYC document must be under 5MB.', 'danger')
                return redirect(url_for('seller.shop_profile'))
            kyc_fn = _save_img(kyc_doc)
            if kyc_fn != 'default.png':
                current_user.kyc_status = 'pending'
                flash('KYC document uploaded. Pending admin review.', 'info')

        db.session.commit()
        flash('Shop profile updated!', 'success')
        return redirect(url_for('seller.shop_profile'))
    return render_template('seller/shop_profile.html', profile=profile)
