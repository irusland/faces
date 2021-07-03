from code.utils import with_performance_profile

import numpy
from PIL.Image import Image


class Painter:
    @with_performance_profile
    def draw_points(self, image: Image, points: numpy.ndarray) -> Image:
        pass
