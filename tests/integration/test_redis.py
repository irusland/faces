import logging
import random
import uuid
from concurrent.futures import Executor, ThreadPoolExecutor

import pytest
from walrus import Walrus

from backend.db.database import FacialData
from backend.db.redis import RedisDB, RedisSettings

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

    @pytest.mark.parametrize(
        "facial_data",
        [
            FacialData(image_hash="123123", landmarks=b"\x02asdasd"),
            FacialData(image_hash="11111111111", landmarks="\x02asdasd"),
            FacialData(image_hash="", landmarks="\000"),
        ],
    )
    def test_simple_get(self, sut_redis, walrus, facial_data):
        key = facial_data.image_hash
        hash_ = walrus.Hash(key)
        hash_.update(facial_data.dict())

        actual = sut_redis.get_landmarks(facial_data.image_hash)

        assert actual == facial_data

    def test_not_found(self, sut_redis):
        actual = sut_redis.get_landmarks(uuid.uuid4().hex)

        assert actual is None


@pytest.fixture()
def executor(request):
    with ThreadPoolExecutor(max_workers=request.param) as executor:
        yield executor


class TestRedisConcurrency:
    def _process_image(
        self, sut_redis: RedisDB, hash_: str, data_size: int
    ) -> FacialData:
        if cached_data := sut_redis.get_landmarks(hash_):
            logger.debug("Got from cache %s", cached_data.image_hash)
            return cached_data
        else:
            random_data = bytes(
                random.getrandbits(8) for _ in range(data_size)
            )
            data = FacialData(image_hash=hash_, landmarks=random_data)
            sut_redis.save_landmarks(data)
            logger.debug("Saved %s", data.image_hash)
            return data

    @pytest.mark.parametrize(
        ("executor", "task_count"),
        [
            (1, 1),
            (1, 10),
            (1, 100),
            (2, 1),
            (2, 2),
            (2, 20),
            (2, 100),
            (3, 1),
            (3, 2),
            (3, 2),
            (3, 9),
            (3, 10),
            (3, 100),
            (10, 10),
            (10, 100),
            (20, 1),
            (20, 10),
            (20, 20),
            (20, 200),
            (1, 1000),
            (2, 1000),
            (3, 1000),
            (4, 1000),
            (5, 1000),
            (10, 1000),
            (20, 1000),
        ],
        indirect=["executor"],
    )
    def test_multi_workers_set(
        self, sut_redis, walrus, executor: Executor, task_count, log
    ):
        data_size = 100
        futures = []

        for i in range(task_count):
            hash_ = uuid.uuid4().hex
            future = executor.submit(
                self._process_image, sut_redis, hash_, data_size
            )
            futures.append(future)
            logger.debug("%s submited", hash_)
        executor.shutdown()

        for future in futures:
            expected = future.result()
            hash_ = walrus.Hash(expected.image_hash)
            dict_ = hash_.as_dict(decode=False)
            dict_ = _decode_dict(dict_)
            actual = FacialData.parse_obj(dict_)
            assert actual == expected


def _decode(s):
    try:
        return s.decode("utf-8") if isinstance(s, bytes) else s
    except UnicodeDecodeError:
        return s


def _decode_dict(d):
    accum = {}
    for key in d:
        accum[_decode(key)] = _decode(d[key])
    return accum
