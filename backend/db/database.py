import abc
import datetime
import logging
from typing import Optional, Tuple

from pydantic import BaseModel

logger = logging.getLogger(__file__)


class ImageData(BaseModel):
    image_hash: str


class FacialData(ImageData):
    landmarks: bytes

    class Config:
        orm_mode = True


class MetaData(ImageData):
    origin_path: str
    save_path: str
    size: Tuple[int, int]
    datetime_original: datetime.datetime


class Database(abc.ABC):
    @abc.abstractmethod
    def save_landmarks(self, data: FacialData) -> Optional[str]:
        ...

    @abc.abstractmethod
    def get_landmarks(self, image_hash: str) -> Optional[FacialData]:
        ...


class MetaDatabase(abc.ABC):
    @abc.abstractmethod
    def save_info(self, data: MetaData) -> Optional[str]:
        ...

    @abc.abstractmethod
    def get_info(self, image_hash: str) -> Optional[MetaData]:
        ...
