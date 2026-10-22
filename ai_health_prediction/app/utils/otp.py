import random
import string
from datetime import datetime, timedelta
from flask_mail import Message
from app import mail, db


def generate_otp():
    """Generate a 6-digit OTP."""
    return "".join(random.choices(string.digits, k=6))


def send_otp_email(user, otp_code):
    """Send OTP to user's email."""
    msg = Message(
        subject="🔐 Your AI Health System Password Reset OTP",
        recipients=[user.email],
        html=f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto;
                    border: 1px solid #e0e0e0; border-radius: 10px; padding: 30px;">
            <h2 style="color: #2c7be5; text-align: center;">AI Health Prediction System</h2>
            <hr style="border: none; border-top: 1px solid #e0e0e0;">
            <p>Hello <strong>{user.full_name}</strong>,</p>
            <p>You requested a password reset. Use the OTP below to reset your password:</p>
            <div style="text-align: center; margin: 30px 0;">
                <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px;
                             color: #2c7be5; background: #f0f6ff; padding: 15px 30px;
                             border-radius: 8px;">{otp_code}</span>
            </div>
            <p style="color: #666;">This OTP is valid for <strong>10 minutes</strong>.</p>
            <p style="color: #666;">If you did not request this, please ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #e0e0e0;">
            <p style="color: #999; font-size: 12px; text-align: center;">
                AI Health Prediction System &copy; 2024
            </p>
        </div>
        """,
    )
    mail.send(msg)


def set_user_otp(user):
    """Generate OTP, save to user, and send email."""
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()
    send_otp_email(user, otp)
    return otp


def verify_otp(user, otp_input):
    """Verify OTP is correct and not expired."""
    if user.otp_code is None:
        return False, "No OTP requested."
    if datetime.utcnow() > user.otp_expiry:
        return False, "OTP has expired. Please request a new one."
    if user.otp_code != otp_input.strip():
        return False, "Invalid OTP. Please try again."
    return True, "OTP verified."
