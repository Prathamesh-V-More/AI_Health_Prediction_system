"""
Image-based disease predictor.
Uses pure Pillow only - no tensorflow required.
Loads keras model only if tensorflow is properly installed.
"""
import os
from PIL import Image

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models_saved", "image_model.h5")

_model  = None
_loaded = False


def _load_model():
    global _model, _loaded
    if _loaded:
        return
    _loaded = True
    if not os.path.exists(MODEL_PATH):
        return
    try:
        import tensorflow as tf
        if not hasattr(tf, 'keras'):
            print("[ImageML] TensorFlow not properly installed, using demo mode.")
            return
        # Try standard load first, then legacy compile=False
        try:
            _model = tf.keras.models.load_model(MODEL_PATH)
        except Exception:
            _model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        print("[ImageML] Model loaded successfully.")
    except Exception as e:
        print(f"[ImageML] Load warning (demo mode active): {e}")


def predict_image(img_path):
    """Returns prediction string from image."""
    _load_model()

    try:
        img = Image.open(img_path).convert("RGB").resize((224, 224))
    except Exception:
        return "Normal"

    if _model is not None:
        try:
            import numpy as np
            arr  = np.array(img, dtype="float32") / 255.0
            arr  = arr.reshape(1, 224, 224, 3)
            pred = float(_model.predict(arr)[0][0])
            return "Pneumonia" if pred > 0.5 else "Normal"
        except Exception as e:
            print(f"[ImageML] Predict error: {e}")

    # Demo mode — brightness heuristic (no ML needed)
    pixels     = list(img.getdata())
    brightness = sum(sum(p) for p in pixels) / (len(pixels) * 3)
    return "Pneumonia" if brightness < 127 else "Normal"
