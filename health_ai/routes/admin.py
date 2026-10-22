id="3xw8r8"
from functools import wraps

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from app import db
from models import Prediction, User


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# ---------------------------------------------------------
# ADMIN ACCESS CONTROL
# ---------------------------------------------------------
def admin_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.admin_login"))

        if session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("prediction.dashboard"))

        return f(*args, **kwargs)

    return decorated


# ---------------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------------
@admin_bp.route("/dashboard")
@admin_required
def dashboard():

    total_users = User.query.filter_by(
        role="user"
    ).count()

    total_predictions = Prediction.query.count()

    symptom_count = Prediction.query.filter_by(
        disease_type="symptoms"
    ).count()

    recent_users = (
        User.query.filter_by(role="user")
        .order_by(User.created_at.desc())
        .limit(10)
        .all()
    )

    recent_preds = (
        Prediction.query
        .order_by(Prediction.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "admin/dashboard.html",

        total_users=total_users,

        total_predictions=total_predictions,

        recent_users=recent_users,

        recent_preds=recent_preds,

        symptom_count=symptom_count,
    )


# ---------------------------------------------------------
# USERS PAGE
# ---------------------------------------------------------
@admin_bp.route("/users")
@admin_required
def users():

    all_users = (
        User.query.filter_by(role="user")
        .order_by(User.created_at.desc())
        .all()
    )

    return render_template(
        "admin/users.html",
        users=all_users
    )


# ---------------------------------------------------------
# PREDICTIONS PAGE
# ---------------------------------------------------------
@admin_bp.route("/predictions")
@admin_required
def predictions():

    page = request.args.get(
        "page",
        1,
        type=int
    )

    pagination = (
        Prediction.query
        .order_by(Prediction.created_at.desc())
        .paginate(
            page=page,
            per_page=15,
            error_out=False
        )
    )

    return render_template(
        "admin/predictions.html",
        predictions=pagination.items,
        pagination=pagination
    )


# ---------------------------------------------------------
# ACTIVATE / DEACTIVATE USER
# ---------------------------------------------------------
@admin_bp.route(
    "/users/<int:user_id>/toggle",
    methods=["POST"]
)
@admin_required
def toggle_user(user_id):

    user = User.query.get_or_404(user_id)

    user.is_active = not user.is_active

    db.session.commit()

    status = (
        "activated"
        if user.is_active
        else "deactivated"
    )

    flash(
        f"User {user.full_name} has been {status}.",
        "success"
    )

    return redirect(url_for("admin.users"))


# ---------------------------------------------------------
# DELETE USER
# ---------------------------------------------------------
@admin_bp.route(
    "/users/<int:user_id>/delete",
    methods=["POST"]
)
@admin_required
def delete_user(user_id):

    user = User.query.get_or_404(user_id)

    Prediction.query.filter_by(
        user_id=user_id
    ).delete()

    db.session.delete(user)

    db.session.commit()

    flash(
        f"User {user.full_name} deleted successfully.",
        "success"
    )

    return redirect(url_for("admin.users"))


# ---------------------------------------------------------
# DATABASE VIEWER
# ---------------------------------------------------------
@admin_bp.route("/database")
@admin_required
def database_viewer():

    from models import OTP

    users = (
        User.query
        .order_by(User.created_at.desc())
        .all()
    )

    predictions = (
        Prediction.query
        .order_by(Prediction.created_at.desc())
        .all()
    )

    otps = (
        OTP.query
        .order_by(OTP.created_at.desc())
        .limit(50)
        .all()
    )

    return render_template(
        "admin/database_viewer.html",
        users=users,
        predictions=predictions,
        otps=otps,
    )

