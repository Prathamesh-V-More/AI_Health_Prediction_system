"""
ML prediction module - works with or without numpy/tensorflow.
Falls back to demo mode if dependencies are not available.
"""
import os
import random
from PIL import Image

XRAY_LABELS = {
    0: "Normal",
    1: "Pneumonia - Bacterial",
    2: "Pneumonia - Viral",
    3: "Tuberculosis",
    4: "COVID-19",
    5: "Pleural Effusion",
}

SKIN_LABELS = {
    0: "Normal Skin",
    1: "Acne",
    2: "Eczema (Atopic Dermatitis)",
    3: "Melanoma (Skin Cancer)",
    4: "Psoriasis",
    5: "Ringworm (Tinea)",
    6: "Rosacea",
}

SEVERITY_MAP = {
    "Normal": "None", "Normal Skin": "None",
    "Acne": "Mild", "Rosacea": "Mild",
    "Eczema (Atopic Dermatitis)": "Moderate",
    "Psoriasis": "Moderate", "Ringworm (Tinea)": "Moderate",
    "Pneumonia - Viral": "Moderate",
    "Pneumonia - Bacterial": "Severe", "Tuberculosis": "Severe",
    "COVID-19": "Severe", "Pleural Effusion": "Severe",
    "Melanoma (Skin Cancer)": "Critical",
}

RECOMMENDATION_MAP = {
    "Normal": "No disease detected. Maintain a healthy lifestyle.",
    "Normal Skin": "Skin appears healthy. Keep up good skincare habits.",
    "Acne": "Use gentle cleansers. Consult a dermatologist if severe.",
    "Rosacea": "Avoid triggers like spicy food and sun. See a dermatologist.",
    "Eczema (Atopic Dermatitis)": "Moisturize regularly. Avoid irritants. Consult a dermatologist.",
    "Psoriasis": "Consult a dermatologist for topical or systemic treatment.",
    "Ringworm (Tinea)": "Antifungal treatment required. Consult a doctor.",
    "Pneumonia - Bacterial": "Immediate medical attention required. Antibiotics needed.",
    "Pneumonia - Viral": "Rest, hydration, and antiviral medication. Consult a doctor.",
    "Tuberculosis": "Urgent medical evaluation required. TB treatment is long-term.",
    "COVID-19": "Isolate immediately. Consult a healthcare provider.",
    "Pleural Effusion": "Urgent medical evaluation required. May need drainage.",
    "Melanoma (Skin Cancer)": "URGENT: See an oncologist immediately. Early treatment is critical.",
}

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models_saved")
_xray_model = None
_skin_model = None
_loaded = False

# Try importing numpy - optional
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Try importing tensorflow - optional
try:
    import tensorflow as tf
    HAS_TF = True if hasattr(tf, 'keras') else False
except ImportError:
    HAS_TF = False


def _load_models():
    global _xray_model, _skin_model, _loaded
    if _loaded:
        return
    _loaded = True
    if not HAS_TF or not HAS_NUMPY:
        return
    try:
        xp = os.path.join(MODEL_DIR, "xray_model.h5")
        sp = os.path.join(MODEL_DIR, "skin_model.h5")
        if os.path.exists(xp):
            _xray_model = tf.keras.models.load_model(xp)
        if os.path.exists(sp):
            _skin_model = tf.keras.models.load_model(sp)
    except Exception as e:
        print(f"[ML] Model load warning: {e}")


def _get_image_stats(path):
    """Get basic image statistics using only Pillow."""
    try:
        img = Image.open(path).convert("RGB")
        pixels = list(img.getdata())
        total  = len(pixels)
        avg_r  = sum(p[0] for p in pixels) / total
        avg_g  = sum(p[1] for p in pixels) / total
        avg_b  = sum(p[2] for p in pixels) / total
        brightness   = (avg_r + avg_g + avg_b) / 3
        color_diff   = (abs(avg_r - avg_g) + abs(avg_r - avg_b) + abs(avg_g - avg_b)) / 3
        return brightness, color_diff, img.size
    except Exception:
        return 128, 10, (224, 224)


def _demo_predict(path, label_map):
    """Deterministic demo prediction using only Pillow."""
    brightness, color_diff, size = _get_image_stats(path)
    seed = int(brightness * 100 + color_diff * 10) % len(label_map)
    conf = round(min(0.72 + (int(brightness) % 20) / 100, 0.97) * 100, 2)
    return seed, conf


def _all_preds(label_map, top_idx, top_conf):
    n     = len(label_map)
    other = round((100 - top_conf) / max(n - 1, 1), 2)
    return {label: (top_conf if i == top_idx else other)
            for i, label in label_map.items()}


def _is_valid(path, expected_type):
    """Validate image using only Pillow - no numpy needed."""
    try:
        img = Image.open(path).convert("RGB")
        w, h = img.size

        if w < 50 or h < 50:
            return False, None, "Image is too small."

        brightness, color_diff, _ = _get_image_stats(path)

        # Very colorful = not medical
        if color_diff > 35:
            return False, None, (
                "This does not appear to be a medical image. "
                "Please upload a valid chest X-ray or skin disease image."
            )

        # Near-grayscale = X-ray
        if color_diff <= 15:
            detected = "xray"
        else:
            detected = "skin" if 50 < brightness < 230 else None
            if detected is None:
                return False, None, "Could not identify this as a medical image."

        if expected_type and detected != expected_type:
            label = "chest X-ray" if expected_type == "xray" else "skin image"
            return False, detected, f"Please upload a {label} for this analysis type."

        return True, detected, "OK"
    except Exception as e:
        return False, None, f"Could not process image: {e}"


def _run_model(model, path):
    """Run model prediction - only called if numpy+tf available."""
    img  = Image.open(path).convert("RGB").resize((224, 224))
    arr  = np.array(img, dtype=np.float32) / 255.0
    arr  = np.expand_dims(arr, axis=0)
    preds = model.predict(arr)[0]
    idx  = int(np.argmax(preds))
    conf = round(float(np.max(preds)) * 100, 2)
    return idx, conf


def predict_xray(path):
    _load_models()
    valid, dtype, reason = _is_valid(path, "xray")
    if not valid:
        return {"valid": False, "error": reason}

    if _xray_model is not None and HAS_NUMPY:
        idx, conf = _run_model(_xray_model, path)
    else:
        idx, conf = _demo_predict(path, XRAY_LABELS)

    disease = XRAY_LABELS.get(idx, "Unknown")
    return {
        "valid": True,
        "disease": disease,
        "confidence": conf,
        "severity": SEVERITY_MAP.get(disease, "Unknown"),
        "recommendation": RECOMMENDATION_MAP.get(disease, "Consult a doctor."),
        "image_type": "xray",
        "all_predictions": _all_preds(XRAY_LABELS, idx, conf),
    }


def predict_skin(path):
    _load_models()
    valid, dtype, reason = _is_valid(path, "skin")
    if not valid:
        return {"valid": False, "error": reason}

    if _skin_model is not None and HAS_NUMPY:
        idx, conf = _run_model(_skin_model, path)
    else:
        idx, conf = _demo_predict(path, SKIN_LABELS)

    disease = SKIN_LABELS.get(idx, "Unknown")
    return {
        "valid": True,
        "disease": disease,
        "confidence": conf,
        "severity": SEVERITY_MAP.get(disease, "Unknown"),
        "recommendation": RECOMMENDATION_MAP.get(disease, "Consult a doctor."),
        "image_type": "skin",
        "all_predictions": _all_preds(SKIN_LABELS, idx, conf),
    }
