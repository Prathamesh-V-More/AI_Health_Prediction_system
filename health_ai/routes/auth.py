import random
import string
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_mail import Message
from app import db, mail
from models import OTP, User

auth_bp = Blueprint("auth", __name__)


def generate_otp():
    return "".join(random.choices(string.digits, k=6))


def send_otp_email(email, otp_code, name=""):
    """Send OTP email. Returns (success, error_message)."""
    try:
        from flask import current_app
        username = current_app.config.get("MAIL_USERNAME", "")
        password = current_app.config.get("MAIL_PASSWORD", "")
        print(f"[MAIL] Sending OTP to {email}, username={username}, pw_len={len(password)}")
        if not username or not password:
            print("[MAIL] Not configured")
            return False, "not_configured"
        msg = Message(
            subject="AI Health System - Password Reset OTP",
            recipients=[email],
            html=f"""
            <div style="font-family:Arial,sans-serif;max-width:500px;margin:auto;
                        border:1px solid #e0e0e0;border-radius:10px;padding:30px;">
              <h2 style="color:#2c7be5;text-align:center;">AI Health Prediction System</h2>
              <hr style="border:none;border-top:1px solid #e0e0e0;">
              <p>Hello <strong>{name or email}</strong>,</p>
              <p>Your OTP for password reset:</p>
              <div style="text-align:center;margin:30px 0;">
                <span style="font-size:36px;font-weight:bold;letter-spacing:8px;
                             color:#2c7be5;background:#f0f6ff;padding:15px 30px;
                             border-radius:8px;">{otp_code}</span>
              </div>
              <p style="color:#666;">Valid for <strong>10 minutes</strong>.</p>
              <p style="color:#666;">If you did not request this, ignore this email.</p>
            </div>
            """,
        )
        mail.send(msg)
        print(f"[MAIL] OTP sent successfully to {email}")
        return True, None
    except Exception as e:
        print(f"[MAIL] Send error: {type(e).__name__}: {e}")
        return False, str(e)


def _handle_otp_flash(sent, err, otp_code):
    """Show success if email sent, show minimal message if failed."""
    if sent:
        flash("OTP has been sent to your email address. Please check your inbox.", "success")
    else:
        flash("Could not send OTP email. Please check your mail configuration in .env file.", "danger")


# ── Home ───────────────────────────────────────────────────────
@auth_bp.route("/")
@auth_bp.route("/home")
def home():
    if "user_id" in session:
        if session.get("role") == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("prediction.dashboard"))
    return render_template("index.html")


# ── Register ───────────────────────────────────────────────────
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("prediction.dashboard"))

    if request.method == "POST":
        full_name        = request.form.get("full_name", "").strip()
        email            = request.form.get("email", "").strip().lower()
        password         = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        age              = request.form.get("age", "").strip()
        gender           = request.form.get("gender", "").strip()
        phone            = request.form.get("phone", "").strip()

        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not email or "@" not in email:
            errors.append("A valid email address is required.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if not age or not age.isdigit() or not (1 <= int(age) <= 120):
            errors.append("Please enter a valid age (1-120).")
        if gender not in ("Male", "Female", "Other"):
            errors.append("Please select a valid gender.")
        if not phone:
            errors.append("Phone number is required.")
        if User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("register.html",
                full_name=full_name, email=email,
                age=age, gender=gender, phone=phone)

        user = User(full_name=full_name, email=email,
                    age=int(age), gender=gender, phone=phone, role="user")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ── Login ──────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        if session.get("role") == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("prediction.dashboard"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("login.html", email=email)

        user = User.query.filter_by(email=email, is_active=True).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html", email=email)

        if user.is_admin():
            flash("Please use the Admin Login page.", "warning")
            return redirect(url_for("auth.admin_login"))

        session.permanent = True
        session["user_id"]   = user.id
        session["user_name"] = user.full_name
        session["user_email"]= user.email
        session["role"]      = "user"

        flash(f"Welcome back, {user.full_name}!", "success")
        return redirect(url_for("prediction.dashboard"))

    return render_template("login.html")


# ── Admin Login ────────────────────────────────────────────────
@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if "user_id" in session and session.get("role") == "admin":
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email, is_active=True, role="admin").first()
        if not user or not user.check_password(password):
            flash("Invalid admin credentials.", "danger")
            return render_template("admin_login.html")

        session.permanent = True
        session["user_id"]   = user.id
        session["user_name"] = user.full_name
        session["user_email"]= user.email
        session["role"]      = "admin"

        flash(f"Welcome, {user.full_name}!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin_login.html")


# ── Logout ─────────────────────────────────────────────────────
@auth_bp.route("/logout")
def logout():
    role = session.get("role", "user")
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.admin_login") if role == "admin" else url_for("auth.login"))


# ── User: Edit Profile ─────────────────────────────────────────
@auth_bp.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        flash("Please log in.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        age       = request.form.get("age", "").strip()
        gender    = request.form.get("gender", "").strip()
        phone     = request.form.get("phone", "").strip()
        new_pw    = request.form.get("new_password", "")
        confirm   = request.form.get("confirm_password", "")

        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if age and (not age.isdigit() or not (1 <= int(age) <= 120)):
            errors.append("Please enter a valid age.")
        if gender and gender not in ("Male", "Female", "Other"):
            errors.append("Please select a valid gender.")
        if new_pw:
            if len(new_pw) < 6:
                errors.append("New password must be at least 6 characters.")
            if new_pw != confirm:
                errors.append("Passwords do not match.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("edit_profile.html", user=user)

        user.full_name = full_name
        if age:
            user.age = int(age)
        if gender:
            user.gender = gender
        if phone:
            user.phone = phone
        if new_pw:
            user.set_password(new_pw)

        db.session.commit()
        session["user_name"] = user.full_name
        flash("Profile updated successfully!", "success")
        return redirect(url_for("prediction.dashboard"))

    return render_template("edit_profile.html", user=user)


# ── Forgot Password (User + Admin) ────────────────────────────
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if not email or "@" not in email:
            flash("Please enter a valid email address.", "danger")
            return render_template("forgot_password.html")

        # Works for both user and admin
        user = User.query.filter_by(email=email, is_active=True).first()
        if not user:
            flash("If that email is registered, an OTP has been sent.", "info")
            session["reset_email"] = email
            return redirect(url_for("auth.verify_otp"))

        OTP.query.filter_by(email=email, is_used=False).update({"is_used": True})
        db.session.commit()

        otp_code = generate_otp()
        otp = OTP(email=email, otp_code=otp_code, expiry_minutes=10)
        db.session.add(otp)
        db.session.commit()

        sent, err = send_otp_email(email, otp_code, user.full_name)
        _handle_otp_flash(sent, err, otp_code)

        session["reset_email"]  = email
        session["reset_role"]   = user.role
        return redirect(url_for("auth.verify_otp"))

    return render_template("forgot_password.html")


# ── Verify OTP ─────────────────────────────────────────────────
@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if "reset_email" not in session:
        flash("Please start the password reset process.", "warning")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        otp_input = request.form.get("otp_code", "").strip()
        email     = session.get("reset_email")

        if not otp_input or len(otp_input) != 6 or not otp_input.isdigit():
            flash("Please enter a valid 6-digit OTP.", "danger")
            return render_template("verify_otp.html")

        otp_record = (OTP.query
                      .filter_by(email=email, otp_code=otp_input, is_used=False)
                      .order_by(OTP.created_at.desc()).first())

        if not otp_record:
            flash("Invalid OTP. Please try again.", "danger")
            return render_template("verify_otp.html")

        if otp_record.is_expired():
            flash("OTP has expired. Please request a new one.", "danger")
            return render_template("verify_otp.html")

        otp_record.is_used = True
        db.session.commit()

        session["otp_verified"] = True
        flash("OTP verified! Please set a new password.", "success")
        return redirect(url_for("auth.reset_password"))

    return render_template("verify_otp.html")


# ── Resend OTP ─────────────────────────────────────────────────
@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    email = session.get("reset_email")
    if not email:
        flash("Session expired. Please start again.", "warning")
        return redirect(url_for("auth.forgot_password"))

    OTP.query.filter_by(email=email, is_used=False).update({"is_used": True})
    db.session.commit()

    otp_code = generate_otp()
    otp = OTP(email=email, otp_code=otp_code, expiry_minutes=10)
    db.session.add(otp)
    db.session.commit()

    user = User.query.filter_by(email=email).first()
    sent, err = send_otp_email(email, otp_code, user.full_name if user else "")
    _handle_otp_flash(sent, err, otp_code)
    return redirect(url_for("auth.verify_otp"))


# ── Reset Password ─────────────────────────────────────────────
@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if "reset_email" not in session or not session.get("otp_verified"):
        flash("Please complete OTP verification first.", "warning")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        new_password     = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(new_password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("reset_password.html")
        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("reset_password.html")

        user = User.query.filter_by(email=session["reset_email"]).first()
        if user:
            user.set_password(new_password)
            db.session.commit()

        role = session.pop("reset_role", "user")
        session.pop("reset_email", None)
        session.pop("otp_verified", None)
        flash("Password reset successfully! Please log in.", "success")
        return redirect(url_for("auth.admin_login") if role == "admin" else url_for("auth.login"))

    return render_template("reset_password.html")


# ── Admin Change Credentials ───────────────────────────────────
@auth_bp.route("/admin/change-credentials", methods=["GET", "POST"])
def admin_change_credentials():
    if "user_id" not in session or session.get("role") != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("auth.admin_login"))

    if request.method == "POST":
        new_email        = request.form.get("new_email", "").strip().lower()
        new_password     = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        current_password = request.form.get("current_password", "")

        admin = User.query.get(session["user_id"])

        if not admin.check_password(current_password):
            flash("Current password is incorrect.", "danger")
            return render_template("admin_change_credentials.html")

        errors = []
        if new_email and "@" not in new_email:
            errors.append("Please enter a valid email address.")
        if new_password and len(new_password) < 6:
            errors.append("New password must be at least 6 characters.")
        if new_password and new_password != confirm_password:
            errors.append("New passwords do not match.")
        if new_email and new_email != admin.email:
            existing = User.query.filter_by(email=new_email).first()
            if existing and existing.id != admin.id:
                errors.append("This email is already in use.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin_change_credentials.html")

        if new_email:
            admin.email = new_email
            session["user_email"] = new_email
        if new_password:
            admin.set_password(new_password)

        db.session.commit()
        flash("Admin credentials updated successfully!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin_change_credentials.html")
