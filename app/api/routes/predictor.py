import io
import json

from core.config import settings
from fastapi import APIRouter, File, HTTPException, UploadFile
from models.prediction import (
    HealthResponse,
    MachineLearningDataInput,
    MachineLearningResponse,
)
from PIL import Image
from services.predict import MachineLearningModelHandlerScore as model

router = APIRouter()  # Creating an APIRouter instance


# Function to get predictions using the ML model
def get_prediction(data_point):
    return model.predict(data_point)


# Endpoint for handling POST requests to '/predict' route
@router.post(
    "/predict",
    response_model=MachineLearningResponse,
    name="predict:get-data",
)
async def predict(lambda_event: MachineLearningDataInput):
    if not lambda_event:
        raise HTTPException(status_code=404, detail="'event' argument invalid!")
    try:
        image_data = lambda_event.get_image()
        final_score = get_prediction(image_data)
        result_dict = {"predicted_label": final_score}
        return MachineLearningResponse(result=result_dict)
    # Handling Exceptions
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except ValueError as err:
        raise HTTPException(status_code=422, detail=f"Unprocessable Entity: {err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {err}")


# Endpoint for handling GET requests to '/health' route
@router.get(
    "/test",
    response_model=MachineLearningResponse,
    name="test:get-data",
)
async def test():
    try:
        lambda_event = MachineLearningDataInput(
            **json.loads(open(settings.INPUT_EXAMPLE, "r").read())
        )
        image_data = lambda_event.get_image()
        final_score = get_prediction(image_data)

        result_dict = {"predicted_label": final_score}
        return MachineLearningResponse(result=result_dict)
    # Returning health status
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except ValueError as err:
        raise HTTPException(status_code=422, detail=f"Unprocessable Entity: {err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {err}")


# @router.get(
#     "/health",
#     response_model=HealthResponse,
#     name="health:get-data",
# )
# async def health():
#     is_health = False
#     try:
#         test_input = MachineLearningDataInput(
#             **json.loads(open(settings.INPUT_EXAMPLE, "r").read())
#         )
#         test_point = test_input.get_np_array()
#         get_prediction(test_point)
#         is_health = True
#         return HealthResponse(status=is_health)
#     except Exception:
#         raise HTTPException(status_code=404, detail="Unhealthy")
