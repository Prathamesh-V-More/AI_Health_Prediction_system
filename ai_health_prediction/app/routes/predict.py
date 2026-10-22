import os
import uuid
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Prediction
from app.utils.predictor import allowed_file, is_valid_medical_image, predict_disease
from app.utils.pdf_report import send_report_email

predict_bp = Blueprint("predict", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../../static/uploads")


def get_upload_folder():
    folder = os.path.join(current_app.static_folder, "uploads")
    os.makedirs(folder, exist_ok=True)
    return folder


@predict_bp.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    if request.method == "POST":
        if "image" not in request.files:
            flash("No file selected.", "danger")
            return redirect(url_for("predict.predict"))

        file = request.files["image"]

        if file.filename == "":
            flash("No file selected.", "danger")
            return redirect(url_for("predict.predict"))

        if not allowed_file(file.filename):
            flash("Invalid file type. Please upload a PNG, JPG, JPEG, BMP, or TIFF image.", "danger")
            return redirect(url_for("predict.predict"))

        # Save file with unique name
        ext = file.filename.rsplit(".", 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        upload_folder = get_upload_folder()
        save_path = os.path.join(upload_folder, unique_name)
        file.save(save_path)

        # Validate medical image
        is_valid, image_type, reason = is_valid_medical_image(save_path)

        if not is_valid:
            os.remove(save_path)
            flash(f"❌ {reason}", "danger")
            return redirect(url_for("predict.predict"))

        # Run prediction
        result = predict_disease(save_path, image_type)

        # Save to database
        prediction = Prediction(
            user_id=current_user.id,
            image_filename=unique_name,
            image_type=image_type,
            predicted_disease=result["disease"],
            confidence=result["confidence"],
            severity=result["severity"],
            recommendation=result["recommendation"],
        )
        db.session.add(prediction)
        db.session.commit()

        # Send PDF report via email (non-blocking attempt)
        try:
            send_report_email(current_user, result, save_path)
            flash("📧 A detailed PDF report has been sent to your email.", "info")
        except Exception as e:
            current_app.logger.warning(f"Email send failed: {e}")
            flash("⚠️ Could not send email report. Check mail configuration.", "warning")

        return render_template(
            "predict_result.html",
            result=result,
            image_filename=unique_name,
            prediction=prediction,
        )

    return render_template("predict.html")
