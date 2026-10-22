from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.utils.otp import set_user_otp, verify_otp
from werkzeug.security import generate_password_hash

auth_bp = Blueprint("auth", __name__)


# ── Register ───────────────────────────────────────────────────
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        age = request.form.get("age", "")
        gender = request.form.get("gender", "")
        phone = request.form.get("phone", "").strip()

        # Validation
        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not email or "@" not in email:
            errors.append("A valid email is required.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if not age.isdigit() or not (1 <= int(age) <= 120):
            errors.append("Please enter a valid age.")
        if gender not in ("Male", "Female", "Other"):
            errors.append("Please select a valid gender.")
        if not phone:
            errors.append("Phone number is required.")

        if User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("auth/register.html", form_data=request.form)

        user = User(
            full_name=full_name,
            email=email,
            age=int(age),
            gender=gender,
            phone=phone,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form_data={})


# ── Login ──────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.full_name}!", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.dashboard"))

    return render_template("auth/login.html")


# ── Logout ─────────────────────────────────────────────────────
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


# ── Forgot Password — Step 1: Enter email ─────────────────────
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        # Always show same message to prevent email enumeration
        if user:
            try:
                set_user_otp(user)
                session["reset_email"] = email
                flash("An OTP has been sent to your email address.", "success")
                return redirect(url_for("auth.verify_otp_page"))
            except Exception as e:
                flash("Failed to send OTP. Please check mail configuration.", "danger")
        else:
            flash("If this email is registered, an OTP will be sent.", "info")
            session["reset_email"] = email
            return redirect(url_for("auth.verify_otp_page"))

    return render_template("auth/forgot_password.html")


# ── Forgot Password — Step 2: Enter OTP ───────────────────────
@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp_page():
    email = session.get("reset_email")
    if not email:
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        otp_input = request.form.get("otp", "").strip()
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User not found.", "danger")
            return redirect(url_for("auth.forgot_password"))

        valid, message = verify_otp(user, otp_input)
        if valid:
            session["otp_verified"] = True
            return redirect(url_for("auth.reset_password"))
        else:
            flash(message, "danger")

    return render_template("auth/verify_otp.html", email=email)


# ── Forgot Password — Step 3: New password ────────────────────
@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if not session.get("otp_verified"):
        return redirect(url_for("auth.forgot_password"))

    email = session.get("reset_email")

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("auth/reset_password.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("auth/reset_password.html")

        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            user.otp_code = None
            user.otp_expiry = None
            db.session.commit()

        session.pop("reset_email", None)
        session.pop("otp_verified", None)
        flash("Password reset successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html")
