import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

model_path = "models_saved/image_model.h5"
try:
    model = tf.keras.models.load_model(model_path, compile=False)
    print("SUCCESS: Loaded with compile=False!")
    print("Input:", model.input_shape)
    print("Output:", model.output_shape)
except Exception as e:
    print(f"compile=False failed: {e}")
    try:
        # Try with custom_objects
        model = tf.keras.models.load_model(
            model_path,
            compile=False,
            custom_objects={"InputLayer": tf.keras.layers.InputLayer}
        )
        print("SUCCESS: Loaded with custom_objects!")
    except Exception as e2:
        print(f"custom_objects failed: {e2}")
        print("Model file is incompatible - needs to be retrained with current TF version")
