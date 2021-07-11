import numpy
import PIL.Image as img
import pyheif
from PIL.Image import Image

from backend.utils import with_performance_profile


class Converter:
    @with_performance_profile
    def pyheif_to_pil_image(self, data: pyheif.HeifFile) -> Image:
        return img.frombytes(
            mode=data.mode, size=data.size, data=data.data
        ).convert("RGB")

    @with_performance_profile
    def pil_image_to_numpy_array(self, image: Image) -> numpy.ndarray:
        return numpy.array(image)

    def pil_image_center(self, image: Image) -> numpy.ndarray:
        w, h = image.size
        return numpy.array([w / 2, h / 2])

    @with_performance_profile
    def numpy_array_to_pil_image(self, image: numpy.ndarray) -> Image:
        return img.fromarray(image)
