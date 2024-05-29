import base64
import json
from io import BytesIO
from typing import List

from fastapi import UploadFile
from PIL import Image
from pydantic import BaseModel


class DetectionResult(BaseModel):
    bbox: List[int]
    class_name: str
    detection_score: float


class ClassificationResult(BaseModel):
    class_name: int
    classification_score: float


class MachineLearningResponse(BaseModel):
    result: dict

    def to_json(self):
        return {
            "statusCode": 200,
            "body": json.dumps({
                "predicted_label": self.result["predicted_label"]
            })
        }


class HealthResponse(BaseModel):
    status: bool


class MachineLearningDataInput(BaseModel):
    event: UploadFile

    def get_image(self):

        image_bytes = self.event["body"].encode("utf-8")
        image = Image.open(BytesIO(base64.b64decode(image_bytes))).convert(mode="L")
        image = image.resize((28, 28))

        return image
