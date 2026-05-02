from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort, jsonify)
from flask_login import login_required, current_user
from app import db
from app.models import (Product, CartItem, Order, Review, Coupon, Notification,
                        SellerProfile, User, Banner, Newsletter, ProductVariant,
                        Shipping, Return)
from app.services.payment import process_checkout
from app.services import shipping_service, return_service, referral_service

customer_bp = Blueprint('customer', __name__)

# ── Storefront / Home ─────────────────────────────────────────────────────────

@customer_bp.route('/')
def home():
    banners      = Banner.query.filter_by(is_active=True).order_by(Banner.position).limit(3).all()
    deals        = (Product.query
                    .filter(Product.discount_percent > 20, Product.stock > 0, Product.status == 'active')
                    .order_by(Product.discount_percent.desc()).limit(8).all())
    new_arrivals = (Product.query
                    .filter(Product.stock > 0, Product.status == 'active')
                    .order_by(Product.created_at.desc()).limit(8).all())
    categories   = [c[0] for c in db.session.query(Product.category).distinct().all()]
    return render_template('customer/home.html',
                           banners=banners, deals=deals,
                           new_arrivals=new_arrivals, categories=categories)


# Keep old index route as alias for backward compat
@customer_bp.route('/index')
def index():
    return redirect(url_for('customer.home'))


# ── Product Listing ───────────────────────────────────────────────────────────

@customer_bp.route('/products/')
def product_listing():
    q    = request.args.get('q', '').strip()
    cat  = request.args.get('category', '')
    minp = request.args.get('min_price', '')
    maxp = request.args.get('max_price', '')
    sort = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)

    qry = Product.query.filter(Product.stock > 0, Product.status == 'active')
    if q:    qry = qry.filter(Product.name.ilike(f'%{q}%'))
    if cat:  qry = qry.filter_by(category=cat)
    if minp:
        try:
            qry = qry.filter(Product.price >= float(minp))
        except ValueError:
            pass
    if maxp:
        try:
            qry = qry.filter(Product.price <= float(maxp))
        except ValueError:
            pass
    if sort == 'price_asc':    qry = qry.order_by(Product.price.asc())
    elif sort == 'price_desc': qry = qry.order_by(Product.price.desc())
    elif sort == 'discount':   qry = qry.order_by(Product.discount_percent.desc())
    else:                      qry = qry.order_by(Product.created_at.desc())

    pagination = qry.paginate(page=page, per_page=20, error_out=False)
    products   = pagination.items

    if sort == 'rating':
        products = sorted(products, key=lambda p: p.avg_rating, reverse=True)

    cats = [c[0] for c in db.session.query(Product.category).distinct().all()]
    return render_template('customer/products.html',
                           products=products, categories=cats,
                           pagination=pagination,
                           q=q, selected_cat=cat,
                           min_price=minp, max_price=maxp, sort=sort)


# ── Product Detail (slug-based) ───────────────────────────────────────────────

@customer_bp.route('/product/<slug>')
def product_detail_slug(slug):
    product  = Product.query.filter_by(slug=slug).first_or_404()
    variants = ProductVariant.query.filter_by(product_id=product.id).all()
    images   = product.image_list
    related  = (Product.query
                .filter(Product.category == product.category,
                        Product.id != product.id,
                        Product.stock > 0)
                .limit(4).all())
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(
            product_id=product.id, user_id=current_user.id).first()
    # Check if user has a delivered order for this product (for return eligibility)
    delivered_order = None
    if current_user.is_authenticated and current_user.role == 'customer':
        from app.models import OrderItem
        oi = (db.session.query(OrderItem)
              .join(Order, Order.id == OrderItem.order_id)
              .filter(OrderItem.product_id == product.id,
                      Order.customer_id == current_user.id,
                      Order.status == 'delivered')
              .first())
        if oi:
            delivered_order = oi.order
    return render_template('customer/product_detail.html',
                           product=product, variants=variants, images=images,
                           related=related, user_review=user_review,
                           delivered_order=delivered_order)


@customer_bp.route('/product/<int:pid>')
def product_detail(pid):
    product = Product.query.get_or_404(pid)
    if product.slug:
        return redirect(url_for('customer.product_detail_slug', slug=product.slug), 301)
    # Fallback for products without slug
    variants = ProductVariant.query.filter_by(product_id=product.id).all()
    images   = product.image_list
    related  = (Product.query
                .filter(Product.category == product.category,
                        Product.id != product.id,
                        Product.stock > 0)
                .limit(4).all())
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(
            product_id=product.id, user_id=current_user.id).first()
    return render_template('customer/product_detail.html',
                           product=product, variants=variants, images=images,
                           related=related, user_review=user_review,
                           delivered_order=None)


# ── Deals ─────────────────────────────────────────────────────────────────────

@customer_bp.route('/deals/')
def deals():
    products = (Product.query
                .filter(Product.discount_percent > 20, Product.stock > 0, Product.status == 'active')
                .order_by(Product.discount_percent.desc()).all())
    return render_template('customer/deals.html', products=products)


# ── New Arrivals ──────────────────────────────────────────────────────────────

@customer_bp.route('/new-arrivals/')
def new_arrivals():
    products = (Product.query
                .filter(Product.stock > 0, Product.status == 'active')
                .order_by(Product.created_at.desc()).limit(40).all())
    return render_template('customer/new_arrivals.html', products=products)


# ── About ─────────────────────────────────────────────────────────────────────

@customer_bp.route('/about/')
def about():
    stats = dict(
        sellers=User.query.filter_by(role='seller').count(),
        customers=User.query.filter_by(role='customer').count(),
        products=Product.query.count(),
        orders=Order.query.count(),
    )
    return render_template('customer/about.html', stats=stats)


# ── Become a Supplier ─────────────────────────────────────────────────────────

@customer_bp.route('/vendors/become-a-supplier/')
def become_supplier():
    stats = dict(
        sellers=User.query.filter_by(role='seller').count(),
        products=Product.query.count(),
        orders=Order.query.count(),
        customers=User.query.filter_by(role='customer').count(),
    )
    return render_template('customer/become_supplier.html', stats=stats)


# ── Newsletter Subscribe ──────────────────────────────────────────────────────

@customer_bp.route('/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    email = request.form.get('email', '').strip().lower()
    if not email or '@' not in email:
        flash('Please enter a valid email address.', 'danger')
        return redirect(request.referrer or url_for('customer.home'))
    existing = Newsletter.query.filter_by(email=email).first()
    if existing:
        if not existing.is_active:
            existing.is_active = True
            db.session.commit()
            flash('Welcome back! You have been re-subscribed.', 'success')
        else:
            flash('You are already subscribed!', 'info')
    else:
        db.session.add(Newsletter(email=email))
        db.session.commit()
        flash('Thank you for subscribing to our newsletter!', 'success')
    return redirect(request.referrer or url_for('customer.home'))


# ── Return Request ────────────────────────────────────────────────────────────

@customer_bp.route('/orders/<int:oid>/return', methods=['POST'])
@login_required
def return_request(oid):
    reason = request.form.get('reason', '').strip()
    if not reason:
        flash('Please provide a reason for the return.', 'danger')
        return redirect(url_for('customer.order_detail', oid=oid))
    try:
        return_service.request_return(oid, current_user.id, reason)
        flash('Return request submitted successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('customer.order_detail', oid=oid))


# ── Reviews ───────────────────────────────────────────────────────────────────

@customer_bp.route('/product/<slug>/review', methods=['POST'])
@login_required
def submit_review(slug):
    product = Product.query.filter_by(slug=slug).first()
    if not product:
        # Try by int id for backward compat
        try:
            pid = int(slug)
            product = Product.query.get_or_404(pid)
        except (ValueError, TypeError):
            abort(404)
    rating  = int(request.form.get('rating', 5))
    comment = request.form.get('comment', '').strip()
    if not 1 <= rating <= 5:
        flash('Rating must be between 1 and 5.', 'danger')
        return redirect(request.referrer or url_for('customer.home'))
    existing = Review.query.filter_by(product_id=product.id, user_id=current_user.id).first()
    if existing:
        existing.rating  = rating
        existing.comment = comment
        flash('Review updated!', 'success')
    else:
        db.session.add(Review(product_id=product.id, user_id=current_user.id,
                              rating=rating, comment=comment))
        flash('Review submitted!', 'success')
    db.session.commit()
    if product.slug:
        return redirect(url_for('customer.product_detail_slug', slug=product.slug))
    return redirect(url_for('customer.product_detail', pid=product.id))


@customer_bp.route('/product/<slug>/review/delete', methods=['POST'])
@login_required
def delete_review(slug):
    product = Product.query.filter_by(slug=slug).first()
    if not product:
        try:
            pid = int(slug)
            product = Product.query.get_or_404(pid)
        except (ValueError, TypeError):
            abort(404)
    review = Review.query.filter_by(product_id=product.id, user_id=current_user.id).first_or_404()
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted.', 'info')
    if product.slug:
        return redirect(url_for('customer.product_detail_slug', slug=product.slug))
    return redirect(url_for('customer.product_detail', pid=product.id))


# ── Cart ──────────────────────────────────────────────────────────────────────

@customer_bp.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(
        (i.variant.price if i.variant_id and i.variant else i.product.price) * i.quantity
        for i in items
    )
    return render_template('customer/cart.html', items=items, total=total)


@customer_bp.route('/cart/add/<int:pid>', methods=['POST'])
@login_required
def add_to_cart(pid):
    p          = Product.query.get_or_404(pid)
    qty        = max(1, int(request.form.get('quantity', 1)))
    variant_id = request.form.get('variant_id', type=int)
    is_ajax    = request.headers.get('X-Requested-With') == 'XMLHttpRequest' \
                 or request.accept_mimetypes.best == 'application/json'

    # Enforce 50-item cart limit
    current_count = CartItem.query.filter_by(user_id=current_user.id).count()
    if current_count >= 50:
        if is_ajax:
            return jsonify(ok=False, message='Cart limit reached (50 items max).')
        flash('Cart limit reached (50 items max).', 'warning')
        return redirect(request.referrer or url_for('customer.cart'))

    variant = None
    if variant_id:
        variant = ProductVariant.query.get(variant_id)
        if not variant or variant.product_id != p.id:
            if is_ajax:
                return jsonify(ok=False, message='Invalid variant selected.')
            flash('Invalid variant selected.', 'danger')
            return redirect(request.referrer or url_for('customer.cart'))
        if variant.stock < qty:
            if is_ajax:
                return jsonify(ok=False, message=f'Only {variant.stock} units available.')
            flash(f'Only {variant.stock} units available for this variant.', 'warning')
            return redirect(request.referrer or url_for('customer.cart'))

    # Find existing cart item (match product + variant)
    ci = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=pid,
        variant_id=variant_id
    ).first()

    if ci:
        max_stock = variant.stock if variant else p.stock
        ci.quantity = min(ci.quantity + qty, max_stock)
    else:
        db.session.add(CartItem(
            user_id=current_user.id,
            product_id=pid,
            quantity=qty,
            variant_id=variant_id,
        ))
    db.session.commit()

    if is_ajax:
        cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
        return jsonify(ok=True, message=f'"{p.name}" added to cart!', cart_count=cart_count)

    flash(f'"{p.name}" added to cart.', 'success')
    return redirect(request.referrer or url_for('customer.cart'))


@customer_bp.route('/cart/update/<int:iid>', methods=['POST'])
@login_required
def update_cart(iid):
    ci = CartItem.query.get_or_404(iid)
    if ci.user_id != current_user.id:
        abort(403)
    qty = int(request.form.get('quantity', 1))
    if qty < 1:
        db.session.delete(ci)
    else:
        max_stock = ci.variant.stock if ci.variant_id and ci.variant else ci.product.stock
        ci.quantity = min(qty, max_stock)
    db.session.commit()
    return redirect(url_for('customer.cart'))


@customer_bp.route('/cart/remove/<int:iid>', methods=['POST'])
@login_required
def remove_from_cart(iid):
    ci = CartItem.query.get_or_404(iid)
    if ci.user_id != current_user.id:
        abort(403)
    db.session.delete(ci)
    db.session.commit()
    flash('Item removed.', 'info')
    return redirect(url_for('customer.cart'))


# ── Coupon validation (AJAX) ──────────────────────────────────────────────────

@customer_bp.route('/coupon/validate', methods=['POST'])
@login_required
def validate_coupon():
    code  = request.form.get('code', '').strip().upper()
    total = float(request.form.get('total', 0))
    coupon = Coupon.query.filter_by(code=code).first()
    if not coupon:
        return jsonify(ok=False, message='Coupon not found.')
    valid, msg = coupon.is_valid(total)
    if not valid:
        return jsonify(ok=False, message=msg)
    discount = coupon.compute_discount(total)
    label = (f'{coupon.discount_value:.0f}% off'
             if coupon.discount_type == 'percent'
             else f'₹{coupon.discount_value:.0f} off')
    return jsonify(ok=True, discount=discount, label=label,
                   new_total=round(total - discount, 2))


# ── Checkout ──────────────────────────────────────────────────────────────────

@customer_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('customer.cart'))

    raw_total = sum(
        (i.variant.price if i.variant_id and i.variant else i.product.price) * i.quantity
        for i in items
    )

    if request.method == 'POST':
        address     = request.form.get('address', '').strip()
        coupon_code = request.form.get('coupon_code', '').strip()
        if not address:
            flash('Please enter a delivery address.', 'danger')
            return redirect(url_for('customer.checkout'))

        order = process_checkout(
            customer_id=current_user.id,
            cart_items=items,
            address=address,
            coupon_code=coupon_code,
        )

        # Create shipping record
        shipping_service.create_shipping(order.id)

        # Trigger referral reward on first order
        if Order.query.filter_by(customer_id=current_user.id).count() == 1:
            referral = current_user.referred_by_rel
            if referral and not referral.reward_given:
                referral_service.credit_referral_reward(referral.id)

        flash(f'Order placed! Ref: {order.payment_ref}', 'success')
        return redirect(url_for('customer.order_detail', oid=order.id))

    return render_template('customer/checkout.html', items=items, total=raw_total)


# ── Orders ────────────────────────────────────────────────────────────────────

@customer_bp.route('/orders')
@login_required
def my_orders():
    orders = (Order.query.filter_by(customer_id=current_user.id)
              .order_by(Order.created_at.desc()).all())
    return render_template('customer/orders.html', orders=orders)


@customer_bp.route('/orders/<int:oid>')
@login_required
def order_detail(oid):
    order = Order.query.get_or_404(oid)
    if order.customer_id != current_user.id and current_user.role != 'admin':
        abort(403)
    # Check return eligibility
    from datetime import datetime, timedelta
    can_return = False
    if order.status == 'delivered':
        existing_return = Return.query.filter(
            Return.order_id == oid,
            Return.status != 'rejected'
        ).first()
        if not existing_return:
            shipping = Shipping.query.filter_by(order_id=oid).first()
            if shipping and shipping.updated_at:
                deadline = shipping.updated_at + timedelta(days=7)
                can_return = datetime.utcnow() <= deadline
            else:
                can_return = True
    return render_template('customer/order_detail.html', order=order, can_return=can_return)


# ── Notifications ─────────────────────────────────────────────────────────────

@customer_bp.route('/notifications')
@login_required
def notifications():
    notifs = (Notification.query
              .filter_by(user_id=current_user.id)
              .order_by(Notification.created_at.desc()).all())
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template('customer/notifications.html', notifications=notifs)


@customer_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False)\
                      .update({'is_read': True})
    db.session.commit()
    return jsonify(ok=True)


# ── Seller store page ─────────────────────────────────────────────────────────

@customer_bp.route('/store/<shop_slug>')
def seller_store(shop_slug):
    profile  = SellerProfile.query.filter_by(shop_slug=shop_slug).first_or_404()
    seller   = profile.user
    q        = request.args.get('q', '').strip()
    cat      = request.args.get('category', '')
    qry      = Product.query.filter_by(seller_id=seller.id).filter(Product.stock > 0)
    if q:    qry = qry.filter(Product.name.ilike(f'%{q}%'))
    if cat:  qry = qry.filter_by(category=cat)
    products = qry.order_by(Product.created_at.desc()).all()
    cats     = [c[0] for c in db.session.query(Product.category)
                .filter_by(seller_id=seller.id).distinct().all()]
    return render_template('customer/seller_store.html',
                           profile=profile, seller=seller,
                           products=products, categories=cats,
                           q=q, selected_cat=cat)
