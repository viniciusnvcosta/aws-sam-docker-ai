# import tensorflow as tf
from core.config import settings
from ultralytics import YOLO


class Utils(object):

    # Load model based on the model format
    def loader(path: str = settings.MODEL_NAME):
        if path.endswith(".pt"):
            return YOLO
        elif path.endswith(".h5"):
            return tf.keras.models.load_model
        else:
            raise ValueError(f"Unsupported model format: {path}")
