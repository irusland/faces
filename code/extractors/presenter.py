import numpy
from cv2 import cv2


class Presenter:
    def display(self, image: numpy.ndarray) -> None:
        image_normalized = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imshow("image", image_normalized)
        cv2.waitKey(0)
