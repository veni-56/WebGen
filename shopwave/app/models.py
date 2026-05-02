from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))


# ── Existing + expanded models ────────────────────────────────────────────────

class SellerProfile(db.Model):
    __tablename__ = 'seller_profiles'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    shop_name   = db.Column(db.String(120), unique=True, nullable=False)
    shop_slug   = db.Column(db.String(120), unique=True, nullable=False)
    logo        = db.Column(db.String(300), default='default.png')
    description = db.Column(db.Text, default='')
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('seller_profile', uselist=False))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(100), nullable=False)
    email          = db.Column(db.String(120), unique=True, nullable=False)
    password       = db.Column(db.String(256), nullable=False)
    role           = db.Column(db.String(20),  default='customer')
    created_at     = db.Column(db.DateTime,    default=datetime.utcnow)

    # ── New columns (task 2.1) ────────────────────────────────────────────────
    mobile         = db.Column(db.String(15),  unique=True, nullable=True)
    referral_code  = db.Column(db.String(20),  unique=True, nullable=True)
    kyc_status     = db.Column(db.String(20),  default='none')   # none|pending|approved|rejected
    is_active      = db.Column(db.Boolean,     default=True)

    products          = db.relationship('Product',           backref='seller',   lazy=True, cascade='all,delete-orphan')
    orders            = db.relationship('Order',             backref='customer', lazy=True)
    cart_items        = db.relationship('CartItem',          backref='user',     lazy=True, cascade='all,delete-orphan')
    seller_earnings   = db.relationship('SellerEarnings',    backref='seller',   lazy=True, cascade='all,delete-orphan')
    notifications     = db.relationship('Notification',      backref='user',     lazy=True, cascade='all,delete-orphan')
    reviews           = db.relationship('Review',            backref='author',   lazy=True, cascade='all,delete-orphan')
    withdrawal_reqs   = db.relationship('WithdrawalRequest', backref='seller',   lazy=True, cascade='all,delete-orphan')
    support_tickets   = db.relationship('SupportTicket',     backref='user',     lazy=True, cascade='all,delete-orphan')
    referrals_made    = db.relationship('Referral', foreign_keys='Referral.referrer_id', backref='referrer', lazy=True)
    referred_by_rel   = db.relationship('Referral', foreign_keys='Referral.referred_id', backref='referred', lazy=True, uselist=False)

    def get_id(self):
        return str(self.id)


class Product(db.Model):
    __tablename__ = 'products'
    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(200), nullable=False)
    description      = db.Column(db.Text)
    price            = db.Column(db.Float,   nullable=False)
    stock            = db.Column(db.Integer, default=0)
    category         = db.Column(db.String(100), default='General')
    image            = db.Column(db.String(300), default='default.png')
    seller_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    # ── New columns (task 2.2) ────────────────────────────────────────────────
    slug             = db.Column(db.String(220), unique=True, nullable=True)
    discount_percent = db.Column(db.Float,   default=0.0)   # 0–100
    images           = db.Column(db.Text,    default='')    # comma-separated filenames
    status           = db.Column(db.String(20), default='active')  # draft|active|inactive

    order_items = db.relationship('OrderItem',      backref='product', lazy=True)
    cart_items  = db.relationship('CartItem',       backref='product', lazy=True, cascade='all,delete-orphan')
    reviews     = db.relationship('Review',         backref='product', lazy=True, cascade='all,delete-orphan')
    variants    = db.relationship('ProductVariant', backref='product', lazy=True, cascade='all,delete-orphan')

    @property
    def avg_rating(self):
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    @property
    def review_count(self):
        return len(self.reviews)

    @property
    def image_list(self):
        """Return list of image filenames (multi-image support)."""
        if self.images:
            return [i.strip() for i in self.images.split(',') if i.strip()]
        return [self.image] if self.image else ['default.png']


# ── New model: ProductVariant (task 2.4) ──────────────────────────────────────

class ProductVariant(db.Model):
    __tablename__ = 'product_variants'
    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    size       = db.Column(db.String(50),  default='')
    color      = db.Column(db.String(50),  default='')
    price      = db.Column(db.Float,       nullable=False)
    stock      = db.Column(db.Integer,     default=0)
    sku        = db.Column(db.String(100), default='')
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)


class Order(db.Model):
    __tablename__ = 'orders'
    id          = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Float,   nullable=False)
    payment_ref = db.Column(db.String(100))
    status      = db.Column(db.String(50), default='pending')
    address     = db.Column(db.Text)
    coupon_code = db.Column(db.String(50))
    discount    = db.Column(db.Float, default=0.0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    items             = db.relationship('OrderItem',         backref='order',  lazy=True, cascade='all,delete-orphan')
    seller_earnings   = db.relationship('SellerEarnings',    backref='order',  lazy=True, cascade='all,delete-orphan')
    platform_earnings = db.relationship('PlatformEarnings',  backref='order',  lazy=True, cascade='all,delete-orphan', uselist=False)
    timeline          = db.relationship('OrderTimeline',     backref='order',  lazy=True, cascade='all,delete-orphan',
                                        order_by='OrderTimeline.created_at')
    shipping          = db.relationship('Shipping',          backref='order',  lazy=True, cascade='all,delete-orphan', uselist=False)
    returns           = db.relationship('Return',            backref='order',  lazy=True, cascade='all,delete-orphan')


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.id'),   nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    seller_id  = db.Column(db.Integer, db.ForeignKey('users.id'),    nullable=False)
    quantity   = db.Column(db.Integer, default=1)
    price      = db.Column(db.Float,   nullable=False)


class OrderTimeline(db.Model):
    __tablename__ = 'order_timeline'
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    status     = db.Column(db.String(50), nullable=False)
    note       = db.Column(db.String(200), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),    nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity   = db.Column(db.Integer, default=1)
    # ── New column (task 2.3) ─────────────────────────────────────────────────
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=True)

    variant = db.relationship('ProductVariant', backref='cart_items', lazy=True)


class SellerEarnings(db.Model):
    __tablename__ = 'seller_earnings'
    id         = db.Column(db.Integer, primary_key=True)
    seller_id  = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount     = db.Column(db.Float,   nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PlatformEarnings(db.Model):
    __tablename__ = 'platform_earnings'
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, unique=True)
    amount     = db.Column(db.Float,   nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    __tablename__ = 'reviews'
    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),    nullable=False)
    rating     = db.Column(db.Integer, nullable=False)
    comment    = db.Column(db.Text,    default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('product_id', 'user_id', name='uq_review_product_user'),
    )


class Coupon(db.Model):
    __tablename__ = 'coupons'
    id             = db.Column(db.Integer, primary_key=True)
    code           = db.Column(db.String(50), unique=True, nullable=False)
    discount_type  = db.Column(db.String(20), default='percent')
    discount_value = db.Column(db.Float,  nullable=False)
    min_order      = db.Column(db.Float,  default=0.0)
    max_uses       = db.Column(db.Integer, default=0)
    used_count     = db.Column(db.Integer, default=0)
    is_active      = db.Column(db.Boolean, default=True)
    expires_at     = db.Column(db.DateTime, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def is_valid(self, cart_total: float) -> tuple[bool, str]:
        if not self.is_active:
            return False, 'Coupon is inactive.'
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False, 'Coupon has expired.'
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False, 'Coupon usage limit reached.'
        if cart_total < self.min_order:
            return False, f'Minimum order ₹{self.min_order:.0f} required.'
        return True, 'OK'

    def compute_discount(self, cart_total: float) -> float:
        if self.discount_type == 'percent':
            return round(cart_total * self.discount_value / 100, 2)
        return min(self.discount_value, cart_total)


class Notification(db.Model):
    __tablename__ = 'notifications'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message    = db.Column(db.String(300), nullable=False)
    link       = db.Column(db.String(200), default='')
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WithdrawalRequest(db.Model):
    __tablename__ = 'withdrawal_requests'
    id         = db.Column(db.Integer, primary_key=True)
    seller_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount     = db.Column(db.Float,   nullable=False)
    upi_id     = db.Column(db.String(100), default='')
    status     = db.Column(db.String(30), default='pending')
    note       = db.Column(db.String(200), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── New models (tasks 2.5 – 2.11) ────────────────────────────────────────────

class OTPCode(db.Model):
    """Mobile OTP for passwordless login (task 2.5)."""
    __tablename__ = 'otp_codes'
    id         = db.Column(db.Integer, primary_key=True)
    mobile     = db.Column(db.String(15), nullable=False)
    code       = db.Column(db.String(6),  nullable=False)
    is_used    = db.Column(db.Boolean,    default=False)
    expires_at = db.Column(db.DateTime,   nullable=False)
    created_at = db.Column(db.DateTime,   default=datetime.utcnow)


class Shipping(db.Model):
    """Shipment tracking per order (task 2.6)."""
    __tablename__ = 'shipping'
    id                 = db.Column(db.Integer, primary_key=True)
    order_id           = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True, nullable=False)
    carrier            = db.Column(db.String(100), default='')
    tracking_number    = db.Column(db.String(100), default='')
    status             = db.Column(db.String(50),  default='pending')
    # pending|dispatched|in_transit|out_for_delivery|delivered|returned
    estimated_delivery = db.Column(db.DateTime, nullable=True)
    updated_at         = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)


class Return(db.Model):
    """Customer return/refund request (task 2.7)."""
    __tablename__ = 'returns'
    id            = db.Column(db.Integer, primary_key=True)
    order_id      = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    customer_id   = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    reason        = db.Column(db.Text,    nullable=False)
    status        = db.Column(db.String(30), default='requested')
    # requested|approved|rejected|refunded
    refund_amount = db.Column(db.Float,   default=0.0)
    admin_note    = db.Column(db.Text,    default='')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = db.relationship('User', foreign_keys=[customer_id], backref='returns')


class Referral(db.Model):
    """Referral tracking (task 2.8)."""
    __tablename__ = 'referrals'
    id           = db.Column(db.Integer, primary_key=True)
    referrer_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    referred_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    reward_given = db.Column(db.Boolean, default=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)


class SupportTicket(db.Model):
    """Support ticket system (task 2.9)."""
    __tablename__ = 'support_tickets'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject     = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text,        nullable=False)
    status      = db.Column(db.String(30),  default='open')    # open|in_progress|resolved|closed
    priority    = db.Column(db.String(20),  default='normal')  # low|normal|high
    admin_reply = db.Column(db.Text,        default='')
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)


class Banner(db.Model):
    """Homepage banner slider (task 2.10)."""
    __tablename__ = 'banners'
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(200), nullable=False)
    image      = db.Column(db.String(300), nullable=False)
    link       = db.Column(db.String(300), default='')
    position   = db.Column(db.Integer,    default=0)
    is_active  = db.Column(db.Boolean,    default=True)
    created_at = db.Column(db.DateTime,   default=datetime.utcnow)


class Newsletter(db.Model):
    """Newsletter subscriber list (task 2.11)."""
    __tablename__ = 'newsletter'
    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active     = db.Column(db.Boolean,  default=True)
