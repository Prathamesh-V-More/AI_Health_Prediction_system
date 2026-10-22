from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(150), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    age           = db.Column(db.Integer, nullable=True)
    gender        = db.Column(db.String(20), nullable=True)
    phone         = db.Column(db.String(20), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    is_active     = db.Column(db.Boolean, default=True)
    role          = db.Column(db.String(20), default="user")  # "user" or "admin"

    predictions   = db.relationship("Prediction", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class OTP(db.Model):
    __tablename__ = "otps"

    id         = db.Column(db.Integer, primary_key=True)
    email      = db.Column(db.String(150), nullable=False)
    otp_code   = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used    = db.Column(db.Boolean, default=False)

    def __init__(self, email, otp_code, expiry_minutes=10):
        self.email      = email
        self.otp_code   = otp_code
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(minutes=expiry_minutes)
        self.is_used    = False

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired()


class Prediction(db.Model):
    __tablename__ = "predictions"

    id                = db.Column(db.Integer, primary_key=True)
    user_id           = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    image_filename    = db.Column(db.String(256), nullable=False)
    disease_type      = db.Column(db.String(20), nullable=False)
    predicted_disease = db.Column(db.String(150), nullable=False)
    confidence        = db.Column(db.Float, nullable=False)
    severity          = db.Column(db.String(50), nullable=True)
    recommendation    = db.Column(db.Text, nullable=True)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Prediction {self.predicted_disease} ({self.confidence}%)>"
