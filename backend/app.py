import logging

from dotenv import load_dotenv

from backend import processor
from backend.container import Container
from backend.processor import process_images
from backend.utils import setup_global_logging
from definitions import DEV_ENV_PATH, PREDICTOR_PATH_68

setup_global_logging()
logger = logging.getLogger(__file__)


if __name__ == "__main__":
    load_dotenv(DEV_ENV_PATH)

    container = Container()
    container.config.model_path.from_value(PREDICTOR_PATH_68)
    container.wire(modules=[processor])
    logger.debug("Container prepared")

    process_images()
