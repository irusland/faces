import logging
from backend.utils import with_performance_profile

import numpy
from PIL.Image import Image
from PIL.ImageDraw import Draw

logger = logging.getLogger(__file__)


class Painter:
    @with_performance_profile
    def draw_points(
        self, image: Image, points: numpy.ndarray, radius: float = 5.1
    ) -> Image:
        draw = Draw(image)
        for x, y in points.tolist():
            draw.regular_polygon(
                bounding_circle=((x, y), radius),  # type: ignore
                n_sides=3,
                fill=(0, 255, 0),
            )
        return image
