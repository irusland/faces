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

    def get_landmarks(self, image_hash: str) -> FacialData:
        pass

    def save_landmarks(self, data: FacialData) -> Optional[str]:
        key = data.image_hash
        hash_ = self._db.Hash(key)
        hash_.update(**data.dict())
        return ""
