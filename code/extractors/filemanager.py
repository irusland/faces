import numpy
from cv2 import cv2

from code.utils import with_performance_profile

import pyheif


class FileManager:
    @with_performance_profile
    def read_heif(self, path: str) -> pyheif.HeifFile:
        with open(path, "rb") as file:
            return pyheif.read(file)

    @with_performance_profile
    def save_np_array_image(self, image: numpy.ndarray, filename: str) -> None:
        cv2.imwrite(filename, image)
