import abc
import logging
import threading
from code.utils import with_performance_profile
from typing import Optional

from pydantic import BaseModel
from pydantic.env_settings import BaseSettings
from tinydb import Query, TinyDB

logger = logging.getLogger(__file__)


class TinyDBSettings(BaseSettings):
    storage_file: str
    landmarks_table_name: str

    class Config:
        env_prefix = "TINY_DB_"


class FacialData(BaseModel):
    image_hash: str
    landmarks: str


class Database(abc.ABC):
    @abc.abstractmethod
    def save_landmarks(self, data: FacialData) -> str:
        ...

    @abc.abstractmethod
    def get_landmarks(self, image_hash: str) -> FacialData:
        ...


class TinyDatabase(Database):
    def __init__(self, settings: TinyDBSettings):
        self._lock = threading.Lock()
        self._db: TinyDB = TinyDB(settings.storage_file)
        self._landmarks_table = self._db.table(settings.landmarks_table_name)

    @with_performance_profile
    def get_landmarks(self, image_hash: str) -> Optional[FacialData]:
        Data = Query()
        self._lock.acquire()
        results = self._landmarks_table.search(Data.image_hash == image_hash)
        self._lock.release()
        if len(results) == 0:
            logger.debug("No records for %s", image_hash)
            return None
        if len(results) > 1:
            logger.warning("Multiple records for %s", image_hash)
        logger.debug("Cache hit for %s", image_hash)
        result, *_ = results
        return FacialData.parse_obj(result)

    @with_performance_profile
    def save_landmarks(self, data: FacialData) -> None:
        self._lock.acquire()
        self._landmarks_table.insert(data.dict())
        logger.info("Saved %s", data.image_hash)
        self._lock.release()
