from core.config import settings
from core.setup import create_application

"""
    The FastAPI application setup.
    This module creates and configures the FastAPI application
    based on the provided settings to deploy the App.
"""

app = create_application(settings=settings)
