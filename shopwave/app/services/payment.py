"""
Payment & Earnings Split Service
=================================
Meesho-style marketplace payment flow:

  1. Validate & apply coupon (if any)
  2. Calculate final total after discount
  3. Create Order + OrderItems
  4. Deduct stock
  5. 90% → SellerEarnings (per seller)
  6. 10% → PlatformEarnings
  7. Record initial OrderTimeline entry
  8. Create Notifications for customer + each seller
  9. Clear cart
"""
import uuid
from collections import defaultdict
from app import db
from app.models import (Order, OrderItem, OrderTimeline, CartItem,
                        SellerEarnings, PlatformEarnings, Coupon, Notification)

SELLER_SHARE   = 0.90
PLATFORM_SHARE = 0.10


def notify(user_id: int, message: str, link: str = '') -> None:
    db.session.add(Notification(user_id=user_id, message=message, link=link))


def process_checkout(customer_id: int, cart_items: list,
                     address: str, coupon_code: str = '') -> Order:
    """
    Full checkout pipeline. Returns committed Order.
    """
    raw_total = sum(ci.product.price * ci.quantity for ci in cart_items)
    discount  = 0.0
    coupon    = None

    # ── Coupon validation & discount ─────────────────────────────────────
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code.upper()).first()
        if coupon:
            valid, _ = coupon.is_valid(raw_total)
            if valid:
                discount = coupon.compute_discount(raw_total)
                coupon.used_count += 1

    final_total = max(0.0, round(raw_total - discount, 2))
    ref = 'PAY-' + uuid.uuid4().hex[:10].upper()

    # ── Create Order ──────────────────────────────────────────────────────
    order = Order(
        customer_id = customer_id,
        total_price = final_total,
        payment_ref = ref,
        status      = 'paid',
        address     = address,
        coupon_code = coupon.code if coupon and discount > 0 else None,
        discount    = discount,
    )
    db.session.add(order)
    db.session.flush()

    # ── OrderItems + stock deduction ──────────────────────────────────────
    seller_totals: dict[int, float] = defaultdict(float)
    seller_ids: set[int] = set()

    for ci in cart_items:
        item_total = ci.product.price * ci.quantity
        db.session.add(OrderItem(
            order_id   = order.id,
            product_id = ci.product_id,
            seller_id  = ci.product.seller_id,
            quantity   = ci.quantity,
            price      = ci.product.price,
        ))
        ci.product.stock = max(0, ci.product.stock - ci.quantity)
        seller_totals[ci.product.seller_id] += item_total
        seller_ids.add(ci.product.seller_id)
        db.session.delete(ci)

    # ── Earnings split ────────────────────────────────────────────────────
    # Proportionally apply discount across sellers
    discount_ratio = discount / raw_total if raw_total > 0 else 0

    for seller_id, amount in seller_totals.items():
        net_amount = amount * (1 - discount_ratio)
        db.session.add(SellerEarnings(
            seller_id = seller_id,
            order_id  = order.id,
            amount    = round(net_amount * SELLER_SHARE, 2),
        ))

    db.session.add(PlatformEarnings(
        order_id = order.id,
        amount   = round(final_total * PLATFORM_SHARE, 2),
    ))

    # ── Order timeline — initial entry ────────────────────────────────────
    db.session.add(OrderTimeline(
        order_id = order.id,
        status   = 'paid',
        note     = f'Order placed. Ref: {ref}' + (f' | Coupon: {coupon.code} (-₹{discount:.2f})' if discount > 0 else ''),
    ))

    # ── Notifications ─────────────────────────────────────────────────────
    notify(customer_id,
           f'Order #{order.id} placed successfully! Ref: {ref}',
           f'/orders/{order.id}')

    for sid in seller_ids:
        notify(sid,
               f'New order #{order.id} received for your product(s).',
               '/seller/orders')

    db.session.commit()
    return order


def record_status_change(order: Order, new_status: str,
                         note: str = '', actor_id: int = None) -> None:
    """
    Update order status and append a timeline entry.
    Call this from any route that changes order status.
    """
    order.status = new_status
    db.session.add(OrderTimeline(
        order_id = order.id,
        status   = new_status,
        note     = note or f'Status changed to {new_status}',
    ))
    # Notify customer
    notify(order.customer_id,
           f'Your order #{order.id} is now {new_status}.',
           f'/orders/{order.id}')
    db.session.commit()
