from enum import Enum
from typing import Any, AnyStr, Literal, Optional, Tuple

import numpy

class VideoCapture:
    def __init__(self, descriptor: int):
        pass
    def set(self, prop_id: int, value: int) -> None:
        pass
    def read(self, image=None): ...

def imshow(name: str, image) -> None:
    pass

def waitKey(delay: Optional[int] = None) -> int:
    pass

COLOR_BGR2RGB: Literal["COLOR_BGR2RGB"]
COLOR_RGB2BGR: Literal["COLOR_RGB2BGR"]

def cvtColor(image: numpy.ndarray, color) -> numpy.ndarray:
    pass

class Buffer:
    def tostring(self) -> bytes: ...

def imencode(
    extension: str, image: numpy.ndarray, params: Optional[Any] = None
) -> Tuple[bool, Buffer]: ...

WINDOW_NORMAL: WindowFlags

class WindowFlags(Enum):
    WINDOW_NORMAL = Literal["WINDOW_NORMAL"]

def namedWindow(winname: str, flags: Optional[WindowFlags] = None) -> None: ...
def circle(
    image,
    center: Tuple[int, int],
    radius: int,
    color: Tuple[int, int, int],
    thickness: int,
) -> None: ...
def fillConvexPoly(img, points, color, lineType=None, shift=None): ...
def convexHull(points, hull=None, clockwise=None, returnPoints=None): ...
