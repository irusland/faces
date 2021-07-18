import logging
import os
import sys
from unittest import mock

import pytest
from dotenv import load_dotenv

from backend.app import main
from backend.container import Container
from backend.db.redis import RedisSettings
from definitions import MODELS_DIR, TEST_ENV_PATH

logger = logging.getLogger(__file__)


@pytest.fixture()
def log(caplog):
    caplog.set_level(logging.DEBUG)
    return caplog


@pytest.fixture()
def connection_pool(redis):
    return redis.connection_pool


@pytest.fixture()
def redis_settings(connection_pool):
    return RedisSettings.parse_obj(connection_pool.connection_kwargs)


@pytest.fixture()
def load_env():
    load_dotenv(TEST_ENV_PATH)
    logger.debug("%s environment loaded", TEST_ENV_PATH)


@pytest.fixture()
def container(load_env):
    container = Container()
    container.config.model_path.from_value(
        os.path.join(MODELS_DIR, "shape_predictor_68_face_landmarks.dat")
    )
    container.config.source_dir.from_env("PHOTOS_SOURCE_DIR")
    container.config.result_dir.from_env("PHOTOS_RESULT_DIR")
    container.config.image_reference_path.from_env("IMAGE_REFERENCE")
    container.wire(modules=[sys.modules[__name__]])
    logger.debug("Container prepared")
    return container


class TestProcessing:
    def test_processing(self, container):
        with container.api_client.override(mock.Mock()):
            main()
