import abc
import datetime
import logging
from typing import Optional, Tuple

from pydantic import BaseModel
from pydantic.class_validators import validator

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
    datetime_original: Optional[datetime.datetime]

    @validator('*', pre=True)
    def none_as_none(cls, v):
        if v == 'None':
            return None
        return v

    @validator('size', pre=True)
    def size_to_tuple(cls, v):
        if isinstance(v, str):
            return eval(v)
        return v

    def __hash__(self):
        return hash(self.image_hash)

    def __eq__(self, other):
        return self.image_hash == other.image_hash


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
