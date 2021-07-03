from typing import Literal

import numpy

class VideoCapture:
    def __init__(self, descriptor: int):
        pass
    def set(self, prop_id: int, value: int) -> None:
        pass

def imshow(name: str, image) -> None:
    pass

def waitKey(timeout: int) -> None:
    pass

COLOR_BGR2RGB: Literal["COLOR_BGR2RGB"]

def cvtColor(image: numpy.ndarray, color) -> numpy.ndarray:
    pass
