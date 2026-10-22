
import os
import uuid
from functools import wraps

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
)

from app import db, mail
from models import Prediction, User
from ml.symptom_predict import (
    predict_from_symptoms,
    get_symptom_categories,
)
from ml.pdf_report import send_report_email

pred_bp = Blueprint("prediction", __name__)


# ─────────────────────────────────────────────────────────────
# LOGIN REQUIRED DECORATOR
# ─────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated


# ─────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────
@pred_bp.route("/dashboard")
@login_required
def dashboard():

    user = User.query.get(session["user_id"])

    recent = (
        Prediction.query.filter_by(user_id=session["user_id"])
        .order_by(Prediction.created_at.desc())
        .limit(5)
        .all()
    )

    categories = get_symptom_categories()

    return render_template(
        "dashboard.html",
        user=user,
        recent_predictions=recent,
        categories=categories,
        show_result=False,
    )


# ─────────────────────────────────────────────────────────────
# SYMPTOM PREDICTION
# ─────────────────────────────────────────────────────────────
@pred_bp.route("/predict", methods=["POST"])
@login_required
def predict():

    symptoms = request.form.getlist("symptoms")

    if len(symptoms) < 2:
        flash("Please select at least 2 symptoms.", "danger")
        return redirect(url_for("prediction.dashboard"))

    result = predict_from_symptoms(symptoms)

    if not result.get("valid", True):
        flash(result.get("error", "Prediction failed."), "danger")
        return redirect(url_for("prediction.dashboard"))

    user = User.query.get(session["user_id"])

    # Save prediction
    record = Prediction(
        user_id=session["user_id"],
        image_filename="symptom_prediction",
        disease_type="symptoms",
        predicted_disease=result["disease"],
        confidence=result["confidence"],
        severity=result.get("severity"),
        recommendation=result.get("recommendation"),
    )

    db.session.add(record)
    db.session.commit()

    # Send PDF Report
    try:
        send_report_email(mail, user, result)
        flash(
            "A detailed PDF report has been sent to your email.",
            "success",
        )

    except Exception as e:
        current_app.logger.warning(f"Email report failed: {e}")

    recent = (
        Prediction.query.filter_by(user_id=session["user_id"])
        .order_by(Prediction.created_at.desc())
        .limit(5)
        .all()
    )

    categories = get_symptom_categories()

    return render_template(
        "dashboard.html",
        user=user,
        recent_predictions=recent,
        categories=categories,
        result=result,
        selected_symptoms=symptoms,
        show_result=True,
    )


# ─────────────────────────────────────────────────────────────
# IMAGE PREDICTION
# ─────────────────────────────────────────────────────────────
@pred_bp.route("/predict-image", methods=["POST"])
@login_required
def predict_image():

    # Check file exists
    if "image" not in request.files:
        flash("No image uploaded.", "danger")
        return redirect(url_for("prediction.dashboard"))

    file = request.files["image"]

    # Check filename
    if file.filename == "":
        flash("Please select an image.", "danger")
        return redirect(url_for("prediction.dashboard"))

    # Generate unique filename
    filename = str(uuid.uuid4()) + "_" + file.filename

    upload_folder = current_app.config["UPLOAD_FOLDER"]

    filepath = os.path.join(upload_folder, filename)

    # Save file
    file.save(filepath)

    # ─────────────────────────────────────────
    # TEMPORARY AI RESULT
    # Replace later with real ML prediction
    # ─────────────────────────────────────────
    result = {
        "disease": "Pneumonia Detected",
        "confidence": 92,
        "severity": "Moderate",
        "recommendation": "Consult a medical professional immediately.",
    }

    user = User.query.get(session["user_id"])

    # Save result in DB
    record = Prediction(
        user_id=session["user_id"],
        image_filename=filename,
        disease_type="xray",
        predicted_disease=result["disease"],
        confidence=result["confidence"],
        severity=result["severity"],
        recommendation=result["recommendation"],
    )

    db.session.add(record)
    db.session.commit()

    recent = (
        Prediction.query.filter_by(user_id=session["user_id"])
        .order_by(Prediction.created_at.desc())
        .limit(5)
        .all()
    )

    categories = get_symptom_categories()

    flash("Image prediction completed successfully.", "success")

    return render_template(
        "dashboard.html",
        user=user,
        recent_predictions=recent,
        categories=categories,
        result=result,
        show_result=True,
    )


# ─────────────────────────────────────────────────────────────
# HISTORY PAGE
# ─────────────────────────────────────────────────────────────
@pred_bp.route("/history")
@login_required
def history():

    page = request.args.get("page", 1, type=int)

    filter_type = request.args.get("filter", "all")

    per_page = 10

    query = Prediction.query.filter_by(
        user_id=session["user_id"]
    )

    if filter_type in ("xray", "skin", "symptoms"):
        query = query.filter_by(disease_type=filter_type)

    pagination = (
        query.order_by(Prediction.created_at.desc())
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )
    )

    user = User.query.get(session["user_id"])

    return render_template(
        "history.html",
        user=user,
        predictions=pagination.items,
        pagination=pagination,
        filter_type=filter_type,
    )

