"""
Return Service — customer return/refund state machine.
Return window: 7 days from delivery.
"""
from datetime import datetime, timedelta
from app import db
from app.models import Return, Order, Notification, Shipping

RETURN_WINDOW_DAYS = 7


def request_return(order_id: int, customer_id: int, reason: str) -> Return:
    """
    Initiate a return request.
    Raises ValueError for invalid state transitions.
    """
    order = Order.query.get(order_id)
    if not order:
        raise ValueError('Order not found.')
    if order.customer_id != customer_id:
        raise ValueError('Not authorised.')
    if order.status != 'delivered':
        raise ValueError('Returns can only be requested for delivered orders.')

    # Check return window (7 days from delivery)
    shipping = Shipping.query.filter_by(order_id=order_id).first()
    if shipping and shipping.updated_at:
        deadline = shipping.updated_at + timedelta(days=RETURN_WINDOW_DAYS)
        if datetime.utcnow() > deadline:
            raise ValueError(f'Return window has expired ({RETURN_WINDOW_DAYS} days from delivery).')

    # Check no active return already exists
    existing = Return.query.filter(
        Return.order_id == order_id,
        Return.status != 'rejected'
    ).first()
    if existing:
        raise ValueError('A return request already exists for this order.')

    ret = Return(
        order_id=order_id,
        customer_id=customer_id,
        reason=reason,
        status='requested',
        refund_amount=order.total_price,
    )
    db.session.add(ret)
    db.session.commit()
    return ret


def process_return(
    return_id: int,
    action: str,          # 'approve' | 'reject' | 'refund'
    refund_amount: float,
    admin_note: str,
    actor_id: int,
) -> Return:
    """
    Admin/seller processes a return request.
    On approval: status → 'approved', customer notified.
    On refund:   status → 'refunded', customer notified.
    On rejection: status → 'rejected', customer notified.
    """
    ret = Return.query.get(return_id)
    if not ret:
        raise ValueError('Return not found.')

    status_map = {'approve': 'approved', 'reject': 'rejected', 'refund': 'refunded'}
    new_status = status_map.get(action)
    if not new_status:
        raise ValueError(f'Unknown action: {action}')

    ret.status       = new_status
    ret.refund_amount = refund_amount
    ret.admin_note   = admin_note
    ret.updated_at   = datetime.utcnow()

    db.session.add(Notification(
        user_id=ret.customer_id,
        message=f'Your return request for order #{ret.order_id} has been {new_status}.',
        link=f'/orders/{ret.order_id}',
    ))
    db.session.commit()
    return ret
