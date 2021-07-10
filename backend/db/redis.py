from typing import Optional

from pydantic.env_settings import BaseSettings
from pydantic.main import Extra
from walrus import Walrus

from backend.db.database import Database, FacialData


class RedisSettings(BaseSettings):
    host: str
    port: int
    db: int

    class Config:
        env_prefix = "REDIS_SETTINGS_"
        extra = Extra.ignore


class RedisDB(Database):
    def __init__(self, settings: RedisSettings):
        self._db = Walrus(
            host=settings.host, port=settings.port, db=settings.db
        )

    def get_landmarks(self, image_hash: str) -> Optional[FacialData]:
        hash_ = self._db.Hash(image_hash)
        if dict_ := hash_.as_dict(decode=False):
            return FacialData.parse_obj(decode_dict(dict_))
        return None

    def save_landmarks(self, data: FacialData) -> Optional[str]:
        key = data.image_hash
        hash_ = self._db.Hash(key)
        return hash_.update(**data.dict())


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
