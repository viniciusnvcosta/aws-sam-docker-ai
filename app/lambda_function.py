import uvicorn

from mangum import Mangum

try:
    from core.config import settings
    from core.setup import create_application
except Exception:
    from app.core.config import settings
    from app.core.setup import create_application


"""
    The FastAPI application setup.
    This module creates and configures the FastAPI application
    based on the provided settings to deploy the App.
"""

# Create the FastAPI application
app = create_application(settings=settings)


@app.get("/ping", status_code=200, response_model=str, tags=["Ping Pong"])
def ping() -> str:
    return "pong"


# Initialize the Mangum handler with the FastAPI app
handler = Mangum(app, lifespan="off")


if __name__ == "__main__":
    uvicorn.run(
        "app.lambda_function:handler", host="0.0.0.0", port="8080", reload=True
    )
