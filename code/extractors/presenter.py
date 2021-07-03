from code.utils import with_performance_profile

from cv2 import cv2
from PIL.Image import Image


class Presenter:
    @with_performance_profile
    def display(self, image: Image) -> None:
        cv2.imshow("image", image)
        cv2.waitKey(0)
