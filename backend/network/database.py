import abc
import logging
from typing import TypeVar

from pydantic import BaseModel

logger = logging.getLogger(__file__)


FaceLandmarks = TypeVar('FaceLandmarks', str, bytes)


class FacialData(BaseModel):
    image_hash: str
    landmarks: FaceLandmarks


class Database(abc.ABC):
    @abc.abstractmethod
    def save_landmarks(self, data: FacialData) -> str:
        ...

    @abc.abstractmethod
    def get_landmarks(self, image_hash: str) -> FacialData:
        ...


