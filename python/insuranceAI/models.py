from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    claims = db.relationship("Claim", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Claim(db.Model):
    __tablename__ = "claims"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    age = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)

    image_filename = db.Column(db.String(255))
    medical_report_filename = db.Column(db.String(255))

    ai_summary = db.Column(db.Text)
    status = db.Column(db.String(20), default="Submitted")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
