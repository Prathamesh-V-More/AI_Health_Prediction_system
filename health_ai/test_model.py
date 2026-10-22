import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

model_path = "models_saved/image_model.h5"
if os.path.exists(model_path):
    try:
        model = tf.keras.models.load_model(model_path)
        print("Model loaded successfully!")
        print("Input shape :", model.input_shape)
        print("Output shape:", model.output_shape)
    except Exception as e:
        print(f"Load error: {e}")
else:
    print("Model file not found at:", model_path)
