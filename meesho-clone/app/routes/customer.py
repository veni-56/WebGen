import uuid
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort, current_app, jsonify)
from flask_login import login_required, current_user
from app import db
from app.models import Product, CartItem, Order, OrderItem, User, SellerProfile, ORDER_STATUSES

customer_bp = Blueprint('customer', __name__)

# ── Homepage / Search / Filter ────────────────────────────────────────────────

@customer_bp.route('/')
def index():
    q         = request.args.get('q', '').strip()
    category  = request.args.get('category', '')
    min_price = request.args.get('min_price', '', type=str).strip()
    max_price = request.args.get('max_price', '', type=str).strip()
    sort      = request.args.get('sort', 'newest')

    query = Product.query.filter(Product.stock > 0)
    if q:
        query = query.filter(Product.name.ilike(f'%{q}%'))
    if category:
        query = query.filter_by(category=category)
    if min_price:
        query = query.filter(Product.price >= float(min_price))
    if max_price:
        query = query.filter(Product.price <= float(max_price))

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    products   = query.all()
    categories = [c[0] for c in db.session.query(Product.category).distinct().all()]
    return render_template('index.html', products=products, categories=categories,
                           q=q, selected_cat=category,
                           min_price=min_price, max_price=max_price, sort=sort)

# ── Product detail ────────────────────────────────────────────────────────────

@customer_bp.route('/product/<int:pid>')
def product_detail(pid):
    product = Product.query.get_or_404(pid)
    related = Product.query.filter(
        Product.category == product.category,
        Product.id != product.id,
        Product.stock > 0
    ).limit(4).all()
    seller_profile = SellerProfile.query.filter_by(user_id=product.seller_id).first()
    return render_template('customer/product_detail.html',
                           product=product, related=related, seller_profile=seller_profile)

# ── Seller storefront ─────────────────────────────────────────────────────────

@customer_bp.route('/shop/<int:seller_id>')
def seller_shop(seller_id):
    seller  = User.query.get_or_404(seller_id)
    if seller.role not in ('seller', 'admin'):
        abort(404)
    profile  = SellerProfile.query.filter_by(user_id=seller_id).first()
    products = Product.query.filter_by(seller_id=seller_id).filter(Product.stock > 0).all()
    return render_template('customer/seller_shop.html',
                           seller=seller, profile=profile, products=products)

# ── Cart ──────────────────────────────────────────────────────────────────────

@customer_bp.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(i.product.price * i.quantity for i in items)
    return render_template('customer/cart.html', items=items, total=total)

@customer_bp.route('/cart/add/<int:pid>', methods=['POST'])
@login_required
def add_to_cart(pid):
    product = Product.query.get_or_404(pid)
    qty     = max(1, int(request.form.get('quantity', 1)))
    item    = CartItem.query.filter_by(user_id=current_user.id, product_id=pid).first()
    if item:
        item.quantity = min(item.quantity + qty, product.stock)
    else:
        db.session.add(CartItem(user_id=current_user.id, product_id=pid, quantity=qty))
    db.session.commit()
    flash(f'"{product.name}" added to cart.', 'success')
    return redirect(request.referrer or url_for('customer.cart'))

@customer_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)
    qty = int(request.form.get('quantity', 1))
    if qty < 1:
        db.session.delete(item)
    else:
        item.quantity = min(qty, item.product.stock)
    db.session.commit()
    return redirect(url_for('customer.cart'))

@customer_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('customer.cart'))

# ── Checkout ──────────────────────────────────────────────────────────────────

@customer_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('customer.cart'))
    total = sum(i.product.price * i.quantity for i in items)

    stripe_pub = current_app.config.get('STRIPE_PUBLIC_KEY', '')
    use_stripe = stripe_pub and not stripe_pub.startswith('pk_test_YOUR')

    if request.method == 'POST':
        address = request.form.get('address', '').strip()
        if not address:
            flash('Please enter a delivery address.', 'danger')
            return redirect(url_for('customer.checkout'))

        pay_method = request.form.get('pay_method', 'dummy')

        if use_stripe and pay_method == 'stripe':
            return _stripe_checkout(items, total, address)

        # ── Dummy payment ──────────────────────────────────────────────────
        payment_ref = 'PAY-' + uuid.uuid4().hex[:10].upper()
        order = _create_order(items, total, address, payment_ref, payment_status='paid', status='confirmed')
        flash(f'Order placed! Ref: {payment_ref}', 'success')
        return redirect(url_for('customer.order_detail', oid=order.id))

    return render_template('customer/checkout.html',
                           items=items, total=total,
                           stripe_pub=stripe_pub, use_stripe=use_stripe)


def _create_order(cart_items, total, address, payment_ref,
                  payment_status='pending', status='pending', stripe_session=None):
    order = Order(
        customer_id=current_user.id,
        total=total,
        status=status,
        payment_status=payment_status,
        address=address,
        payment_ref=payment_ref,
        stripe_session=stripe_session
    )
    db.session.add(order)
    db.session.flush()
    for item in cart_items:
        db.session.add(OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        ))
        item.product.stock = max(0, item.product.stock - item.quantity)
        db.session.delete(item)
    db.session.commit()
    return order


def _stripe_checkout(items, total, address):
    import stripe
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    line_items = [{
        'price_data': {
            'currency': 'inr',
            'product_data': {'name': i.product.name},
            'unit_amount': int(i.product.price * 100),
        },
        'quantity': i.quantity,
    } for i in items]
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('customer.stripe_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('customer.checkout', _external=True),
            metadata={'address': address, 'user_id': str(current_user.id)}
        )
        # Save a pending order linked to this session
        order = _create_order(items, total, address,
                              payment_ref=session.payment_intent or session.id,
                              payment_status='pending', status='pending',
                              stripe_session=session.id)
        return redirect(session.url, code=303)
    except Exception as e:
        flash(f'Stripe error: {e}', 'danger')
        return redirect(url_for('customer.checkout'))


@customer_bp.route('/checkout/success')
@login_required
def stripe_success():
    session_id = request.args.get('session_id')
    if session_id:
        import stripe
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            order = Order.query.filter_by(stripe_session=session_id).first()
            if order and session.payment_status == 'paid':
                order.payment_status = 'paid'
                order.status         = 'confirmed'
                db.session.commit()
                flash(f'Payment successful! Order #{order.id} confirmed.', 'success')
                return redirect(url_for('customer.order_detail', oid=order.id))
        except Exception as e:
            flash(f'Could not verify payment: {e}', 'warning')
    flash('Order placed!', 'success')
    return redirect(url_for('customer.my_orders'))

# ── Orders ────────────────────────────────────────────────────────────────────

@customer_bp.route('/orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('customer/orders.html', orders=orders)

@customer_bp.route('/orders/<int:oid>')
@login_required
def order_detail(oid):
    order = Order.query.get_or_404(oid)
    if order.customer_id != current_user.id and current_user.role != 'admin':
        abort(403)
    return render_template('customer/order_detail.html', order=order, statuses=ORDER_STATUSES)
