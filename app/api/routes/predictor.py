import json

from core.config import settings
from fastapi import APIRouter, HTTPException
from models.prediction import (
    MachineLearningDataInput,
    MachineLearningResponse,
)
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
        image_point = lambda_event.get_image()
        prediction = get_prediction(image_point)

        result = {"predicted_label": prediction}
        return MachineLearningResponse(result=result)
    # Handling Exceptions
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except ValueError as err:
        raise HTTPException(status_code=422, detail=f"Unprocessable Entity: {err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {err}")


# Endpoint for handling GET requests to a 'health'-like route
@router.get(
    "/test",
    response_model=MachineLearningResponse,
    name="test:get-data",
)
async def test():
    is_health = False
    try:
        lambda_event = MachineLearningDataInput(
            **json.loads(open(settings.INPUT_EXAMPLE, "r").read())
        )
        image_point = lambda_event.get_image()
        prediction = get_prediction(image_point)

        is_health = True
        result = {
            "predicted_label": prediction,
            "is_healthy": is_health,
        }
        return MachineLearningResponse(result=result)
    # Returning unhealth status
    except Exception as err:
        raise HTTPException(status_code=404, detail=f"Unhealthy: {err}")
