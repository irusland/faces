from code.utils import with_performance_profile

import numpy
import PIL.Image as img
import pyheif
from PIL.Image import Image


class Converter:
    @with_performance_profile
    def pyheif_to_pil_image(self, data: pyheif.HeifFile) -> Image:
        return img.frombytes(
            mode=data.mode, size=data.size, data=data.data
        ).convert("RGB")

    @with_performance_profile
    def pil_image_to_numpy_array(self, image: Image) -> numpy.ndarray:
        return numpy.array(image)

    @with_performance_profile
    def numpy_array_to_pil_image(self, image: numpy.ndarray) -> Image:
        return img.fromarray(image)
