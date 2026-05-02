"""
Shipping Service — create and update shipment records.
Called from checkout (create) and seller/admin routes (update).
"""
from datetime import datetime
from app import db
from app.models import Shipping, Order, Notification


def create_shipping(order_id: int) -> Shipping:
    """
    Create a Shipping record for a newly placed order.
    Called immediately after order creation in checkout.
    """
    existing = Shipping.query.filter_by(order_id=order_id).first()
    if existing:
        return existing
    shipping = Shipping(order_id=order_id, status='pending')
    db.session.add(shipping)
    db.session.commit()
    return shipping


def update_tracking(
    order_id: int,
    carrier: str,
    tracking_number: str,
    status: str,
    estimated_delivery: datetime | None = None,
) -> Shipping:
    """
    Update shipment tracking info.
    If status becomes 'delivered':
      - Sets Order.status = 'delivered'
      - Settles seller earnings (credits wallet)
      - Notifies customer
    """
    shipping = Shipping.query.filter_by(order_id=order_id).first()
    if not shipping:
        shipping = Shipping(order_id=order_id)
        db.session.add(shipping)

    shipping.carrier         = carrier
    shipping.tracking_number = tracking_number
    shipping.status          = status
    shipping.estimated_delivery = estimated_delivery
    shipping.updated_at      = datetime.utcnow()

    if status == 'delivered':
        order = Order.query.get(order_id)
        if order and order.status != 'delivered':
            order.status = 'delivered'
            # Settle seller earnings
            _settle_earnings(order)
            # Notify customer
            db.session.add(Notification(
                user_id=order.customer_id,
                message=f'Your order #{order.id} has been delivered!',
                link=f'/orders/{order.id}',
            ))

    db.session.commit()
    return shipping


def _settle_earnings(order: Order) -> None:
    """Credit seller wallet for each SellerEarnings row on this order."""
    from app.models import SellerEarnings, User
    for earning in order.seller_earnings:
        seller = User.query.get(earning.seller_id)
        if seller:
            db.session.add(Notification(
                user_id=seller.id,
                message=f'₹{earning.amount:.2f} credited for order #{order.id}.',
                link='/seller/earnings',
            ))
