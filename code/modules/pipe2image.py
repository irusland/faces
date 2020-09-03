import sys
import cv2
import numpy


def get_image(buffer):
    array = numpy.frombuffer(buffer, numpy.uint8)
    return cv2.imdecode(array, 1)


if __name__ == '__main__':
    buffer = sys.stdin.buffer
    get_image(buffer)
