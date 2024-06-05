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

    # def to_json(self):
    #     return {
    #         "statusCode": 200,
    #         "body": json.dumps({"predicted_label": self.result["predicted_label"]}),
    #     }


class HealthResponse(BaseModel):
    status: bool


class MachineLearningDataInput(BaseModel):
    resource: str
    path: str
    httpMethod: str
    isBase64Encoded: bool
    pathParameters: dict
    stageVariables: dict
    headers: dict
    requestContext: dict
    body: str

    def get_image(self):
        try:
            image_bytes = self.body.encode("utf-8")
            image = Image.open(BytesIO(base64.b64decode(image_bytes))).convert(mode="L")
            image = image.resize((28, 28))
            return image
        except KeyError:
            raise ValueError("Invalid input data: 'body' key is missing")
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")
