from typing import Callable

from services.utils import Utils as utils
from fastapi import FastAPI
from loguru import logger


def preload_model():
    """
    In order to load model on memory to each worker
    """
    from services.predict import MachineLearningModelHandlerScore

    MachineLearningModelHandlerScore.get_model(load_wrapper=utils.loader())


def create_start_app_handler(app: FastAPI) -> Callable:
    def start_app() -> None:
        preload_model()
        logger.info("Model preloaded to memory")

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    def stop_app() -> None:
        # TODO drop app resources
        logger.info("Application stopped")

    return stop_app
