from typing import Any, Union

from fastapi import FastAPI

from api.routes.api import router as api_router
from core.events import create_start_app_handler, create_stop_app_handler

# from core.config import API_PREFIX, DEBUG, PROJECT_NAME, VERSION
from core.config import AppSettings, CryptSettings


def create_application(
    settings: Union[AppSettings, CryptSettings],
    **kwargs: Any,
) -> FastAPI:
    """
    Creates and configures a FastAPI application based on the provided settings.

    This function initializes a FastAPI application and configures it with various settings
    and handlers based on the type of the `settings` object provided.

    Parameters
    ----------

    **kwargs
        Additional keyword arguments passed directly to the FastAPI constructor.

    settings
        An instance representing the settings for configuring the FastAPI application.
        It determines the configuration applied:

        - AppSettings: Configures basic app metadata like name, description, contact, and license info.
        - CryptSettings: Configures security settings like secret key, algorithm, and token expiration.

    Returns
    -------
    FastAPI
        A fully configured FastAPI application instance.

    The function configures the FastAPI application with different features and behaviors
    based on the provided settings. It includes setting up database connections, Redis pools
    for caching, queue, and rate limiting, client-side caching, and customizing the API documentation
    based on the environment settings.
    """

    # --- before app creation ---
    if isinstance(settings, AppSettings):
        kwargs = {
            "title": settings.APP_NAME,
            "license_info": {
                "name": settings.LICENSE_NAME,
            },
            "description": settings.APP_DESCRIPTION,
            "debug": settings.DEBUG,
            "version": settings.APP_VERSION,
            **kwargs,
        }

    # TODO --- before app creation ---
    if isinstance(settings, CryptSettings):
        pass

    # --- app creation ---
    application = FastAPI(**kwargs)
    application.include_router(api_router, prefix=settings.API_PREFIX)
    pre_load = False
    if pre_load:
        application.add_event_handler("startup", create_start_app_handler(application))
        application.add_event_handler("shutdown", create_stop_app_handler(application))

    return application
