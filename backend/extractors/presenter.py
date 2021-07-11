import numpy
from cv2 import cv2
from PIL import Image


class Presenter:
    def display(self, image: numpy.ndarray) -> None:
        image_normalized = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imshow("image", image_normalized)
        cv2.waitKey(0)

    def show(
        self,
        painter,
        pil_image: Image.Image,
        face_landmarks,
        anchor_size,
    ):
        if anchor_size:
            pil_image = pil_image.resize(anchor_size, Image.ANTIALIAS)
        painter.draw_points(pil_image, face_landmarks)
        pil_image.show()
