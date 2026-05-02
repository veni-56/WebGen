from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    role       = db.Column(db.String(20),  default='customer')  # admin | seller | customer
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

    products    = db.relationship('Product',       backref='seller',   lazy=True, cascade='all, delete-orphan')
    orders      = db.relationship('Order',         backref='customer', lazy=True)
    cart_items  = db.relationship('CartItem',      backref='user',     lazy=True, cascade='all, delete-orphan')
    profile     = db.relationship('SellerProfile', backref='user',     uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username} [{self.role}]>'


class SellerProfile(db.Model):
    """Extended profile for seller accounts."""
    __tablename__ = 'seller_profiles'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    shop_name   = db.Column(db.String(150), default='')
    shop_logo   = db.Column(db.String(300), default='default.png')
    description = db.Column(db.Text,        default='')
    # Cumulative earnings (updated when order is delivered)
    earnings    = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<SellerProfile {self.shop_name}>'


class Product(db.Model):
    __tablename__ = 'products'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price       = db.Column(db.Float,   nullable=False)
    stock       = db.Column(db.Integer, default=0)
    category    = db.Column(db.String(100), default='General')
    image       = db.Column(db.String(300), default='default.png')
    seller_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    cart_items  = db.relationship('CartItem',  backref='product', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Product {self.name}>'


# Order status flow: pending → confirmed → shipped → delivered | cancelled
ORDER_STATUSES = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']

class Order(db.Model):
    __tablename__ = 'orders'
    id             = db.Column(db.Integer, primary_key=True)
    customer_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total          = db.Column(db.Float,   nullable=False)
    status         = db.Column(db.String(50), default='pending')
    payment_status = db.Column(db.String(50), default='pending')  # pending | paid | failed | refunded
    address        = db.Column(db.Text)
    payment_ref    = db.Column(db.String(200))   # Stripe PaymentIntent id or dummy ref
    stripe_session = db.Column(db.String(200))   # Stripe Checkout Session id
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order #{self.id} {self.status}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.id'),   nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity   = db.Column(db.Integer, default=1)
    price      = db.Column(db.Float,   nullable=False)  # price snapshot at purchase time


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),    nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity   = db.Column(db.Integer, default=1)
