from datetime import datetime, timedelta

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Rate limiting / account lockout (new in Day5)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)

    cart_items = db.relationship("CartItem", backref="user", cascade="all, delete-orphan")
    orders = db.relationship("Order", backref="user", cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def is_locked(self):
        return self.locked_until is not None and self.locked_until > datetime.utcnow()

    def register_failed_login(self, max_attempts, lockout_minutes):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            self.locked_until = datetime.utcnow() + timedelta(minutes=lockout_minutes)

    def register_successful_login(self):
        self.failed_login_attempts = 0
        self.locked_until = None


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.Integer, nullable=True)  # id from dummyjson.com, if synced
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    product = db.relationship("Product")

    __table_args__ = (db.UniqueConstraint("user_id", "product_id", name="uq_cart_user_product"),)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default="placed", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)

    product = db.relationship("Product")


class PasswordResetOTP(db.Model):
    __tablename__ = "password_reset_otps"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User")

    def is_valid(self):
        return not self.used and self.expires_at > datetime.utcnow()
