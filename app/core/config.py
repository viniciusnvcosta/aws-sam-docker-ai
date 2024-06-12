import logging
import os
import sys
from enum import Enum
from dotenv import load_dotenv
from loguru import logger
from core.logging import InterceptHandler
from pydantic_settings import BaseSettings
from starlette.config import Config
from starlette.datastructures import Secret

load_dotenv()
current_file_dir = os.path.dirname(os.path.realpath(__file__))
env_path = os.path.join(current_file_dir, "..", "..", ".env")
config = Config(env_path)


class AppSettings(BaseSettings):
    APP_NAME: str = config("PROJECT_NAME", default="insert_name-ia")
    APP_DESCRIPTION: str | None = config("APP_DESCRIPTION", default=None)
    APP_VERSION: str | None = config("APP_VERSION", default="0.1.0")
    API_PREFIX: str | None = config("API_PREFIX", default="/api")
    if not API_PREFIX.startswith("/"):
        API_PREFIX = "/" + API_PREFIX
    DEBUG: bool = config("DEBUG", cast=bool, default=False)
    CONTACT_NAME: str | None = config("CONTACT_NAME", default=None)
    CONTACT_EMAIL: str | None = config("CONTACT_EMAIL", default=None)
    LICENSE_NAME: str | None = config("LICENSE", default=None)
    # logging configuration
    LOGGING_LEVEL: int = logging.DEBUG if DEBUG else logging.INFO  # Add type annotation
    logging.basicConfig(
        handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
    )
    logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])


class CryptSettings(BaseSettings):
    SECRET_KEY: str = config("SECRET_KEY", default="")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7)


class EnvironmentOption(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseSettings):
    # ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default="local")
    MODEL_PATH: str = config("MODEL_PATH", default="/opt/ml/")
    MODEL_NAME: str = config("MODEL_NAME", default="model")
    INPUT_EXAMPLE: str = config("INPUT_EXAMPLE", default="./events/event.json")
    IMG_SIZE: int = config("IMG_SIZE", default=640)


class S3ConnectionSettings(BaseSettings):
    S3_BUCKET_NAME: str = config("S3_BUCKET_NAME", default="")
    S3_ACCESS_KEY: str = config("S3_ACCESS_KEY", default="")
    S3_SECRET_KEY: str = config("S3_SECRET_KEY", default="")


# ? not sure if needed in future
# class DefaultRateLimitSettings(BaseSettings):
#     DEFAULT_RATE_LIMIT_LIMIT: int = config("DEFAULT_RATE_LIMIT_LIMIT", default=10)
#     DEFAULT_RATE_LIMIT_PERIOD: int = config("DEFAULT_RATE_LIMIT_PERIOD", default=3600)
#     MAX_CONNECTIONS_COUNT: int = config("MAX_CONNECTIONS_COUNT", cast=int, default=10)
#     MIN_CONNECTIONS_COUNT: int = config("MIN_CONNECTIONS_COUNT", cast=int, default=10)


class Settings(
    AppSettings,
    CryptSettings,
    EnvironmentSettings,
    S3ConnectionSettings,
):
    pass


# use this to import settings in other modules
settings = Settings()
