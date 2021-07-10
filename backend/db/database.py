import abc
import logging
from typing import Optional

from pydantic import BaseModel

logger = logging.getLogger(__file__)


class FacialData(BaseModel):
    image_hash: str
    landmarks: bytes

    class Config:
        orm_mode = True


class Database(abc.ABC):
    @abc.abstractmethod
    def save_landmarks(self, data: FacialData) -> Optional[str]:
        ...

    @abc.abstractmethod
    def get_landmarks(self, image_hash: str) -> Optional[FacialData]:
        ...
