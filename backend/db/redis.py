from typing import Optional, Type, TypeVar

from pydantic.env_settings import BaseSettings
from pydantic.main import Extra
from walrus import Walrus

from backend.db.database import (
    Database,
    FacialData,
    ImageData,
    MetaData,
    MetaDatabase,
)


class RedisSettings(BaseSettings):
    host: str
    port: int
    db: int = 0
    meta_info_db: int = 1

    class Config:
        env_prefix = "REDIS_SETTINGS_"
        extra = Extra.ignore


DataType = TypeVar("DataType", bound=ImageData)


class RedisDB(Database, MetaDatabase):
    def __init__(self, settings: RedisSettings):
        self._db = Walrus(
            host=settings.host, port=settings.port, db=settings.db
        )
        self._meta_info_db = Walrus(
            host=settings.host, port=settings.port, db=settings.meta_info_db
        )

    def _get(
        self, db: Walrus, item_hash_: str, model: Type[DataType]
    ) -> Optional[DataType]:
        hash_ = db.Hash(item_hash_)
        if dict_ := hash_.as_dict(decode=False):
            return model.parse_obj(decode_dict(dict_))
        return None

    def _update(self, db: Walrus, data: ImageData) -> Optional[str]:
        key = data.image_hash
        hash_ = db.Hash(key)
        return hash_.update(**data.dict())

    def get_landmarks(self, image_hash: str) -> Optional[FacialData]:
        return self._get(self._db, image_hash, FacialData)

    def save_landmarks(self, data: FacialData) -> Optional[str]:
        return self._update(self._db, data)

    def get_info(self, item_hash: str) -> Optional[MetaData]:
        return self._get(self._meta_info_db, item_hash, MetaData)

    def save_info(self, data: MetaData) -> Optional[str]:
        return self._update(self._db, data)


def _decode(s):
    try:
        return s.decode("utf-8") if isinstance(s, bytes) else s
    except UnicodeDecodeError:
        return s


def decode_dict(d):
    accum = {}
    for key in d:
        accum[_decode(key)] = _decode(d[key])
    return accum
