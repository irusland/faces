import logging

import pytest
from dotenv import load_dotenv

from backend.container import Container
from backend.db.redis import RedisDB, RedisSettings
from definitions import PREDICTOR_PATH_68, TEST_ENV_PATH

logger = logging.getLogger(__file__)


@pytest.fixture()
def connection_pool(redis):
    return redis.connection_pool


@pytest.fixture()
def redis_settings(connection_pool):
    return RedisSettings.parse_obj(connection_pool.connection_kwargs)


@pytest.fixture()
def test_redis(redis_settings):
    return RedisDB(redis_settings)


@pytest.fixture()
def load_env():
    load_dotenv(TEST_ENV_PATH)
    logger.debug("%s environment loaded", TEST_ENV_PATH)


@pytest.fixture()
def container(load_env, redis_settings, test_redis):
    container = Container()
    container.config.model_path.from_value(PREDICTOR_PATH_68)

    with container.db_settings.override(redis_settings):
        logger.debug("Container prepared")
        yield container
