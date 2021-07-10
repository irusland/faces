import logging
from backend.extractors.converter import Converter
from backend.utils import with_performance_profile
from functools import singledispatchmethod
from typing import Literal, Union

import magic
import numpy
import PIL
import pyheif
from cv2 import cv2
from PIL.Image import Image
from pydantic.main import BaseModel
from pydantic.tools import parse_obj_as

logger = logging.getLogger(__file__)


class Extension(BaseModel):
    extension: str


class JPEG(Extension):
    extension: Literal["image/jpeg"]


class PNG(Extension):
    extension: Literal["image/png"]


class HEIC(Extension):
    extension: Literal["image/heic"]


Supported = Union[JPEG, PNG, HEIC]


class FileManager:
    def __init__(self, converter: Converter):
        self._converter = converter

    def _get_supported(self, path: str) -> Extension:
        mime = magic.from_file(path, mime=True)
        return parse_obj_as(Supported, dict(extension=mime))  # type: ignore

    @with_performance_profile
    def read_pil_auto(self, path: str) -> Image:
        extension = self._get_supported(path)
        logger.debug("Got %s %s", extension, path)
        return self._read(extension, path)

    @singledispatchmethod
    def _read(self, extension: Extension, path: str) -> Image:
        raise RuntimeError(f"cannot read {extension} for {path}")

    @_read.register
    def _read_jpeg(self, extension: JPEG, path: str) -> Image:
        return PIL.Image.open(path).convert("RGB")

    @_read.register
    def _read_png(self, extension: PNG, path: str) -> Image:
        return PIL.Image.open(path).convert("RGB")

    @_read.register
    def _read_heic(self, extension: HEIC, path: str) -> Image:
        heif_image = self.read_heif(path)
        return self._converter.pyheif_to_pil_image(heif_image)

    @with_performance_profile
    def read_heif(self, path: str) -> pyheif.HeifFile:
        with open(path, "rb") as file:
            return pyheif.read(file)

    @with_performance_profile
    def save_np_array_image(self, image: numpy.ndarray, filename: str) -> None:
        cv2.imwrite(filename, image)
