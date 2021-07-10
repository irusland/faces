import pytest
from walrus import Walrus

from backend.db.database import FacialData
from backend.db.redis import RedisDB, RedisSettings


@pytest.fixture()
def connection_pool(redis):
    return redis.connection_pool


@pytest.fixture()
def redis_settings(connection_pool):
    return RedisSettings.parse_obj(connection_pool.connection_kwargs)


@pytest.fixture()
def sut_redis(redis_settings):
    return RedisDB(redis_settings)


@pytest.fixture()
def walrus(redis_settings):
    return Walrus(
        host=redis_settings.host,
        port=redis_settings.port,
        db=redis_settings.db,
    )


class TestRedis:
    @pytest.mark.parametrize(
        "facial_data",
        [
            FacialData(image_hash="123123", landmarks=b"\x02asdasd"),
            FacialData(image_hash="11111111111", landmarks="\x02asdasd"),
            FacialData(image_hash="", landmarks="\000"),
        ],
    )
    def test_simple_add(self, sut_redis, walrus, facial_data):
        sut_redis.save_landmarks(facial_data)

        hash_ = walrus.Hash(facial_data.image_hash)
        dict_ = hash_.as_dict(decode=True)
        actual = FacialData.parse_obj(dict_)
        assert actual == facial_data
