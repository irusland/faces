import pytest
from db.database import FacialData
from db.redis import RedisDB, RedisSettings
from walrus import Walrus


@pytest.fixture()
def redis_settings():
    return RedisSettings(host="localhost", port=6379, db=0)


@pytest.fixture()
def redis(redis_settings):
    return RedisDB(redis_settings)


@pytest.fixture()
def raw_redis(redis_settings):
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
    def test_simple_add(self, redis, raw_redis, facial_data):
        redis.save_landmarks(facial_data)
        hash_ = raw_redis.Hash(facial_data.image_hash)
        dict_ = hash_.as_dict(decode=True)
        actual = FacialData.parse_obj(dict_)
        assert actual == facial_data
