import sys

import cv2

from pipe2image import get_image
from corrector import Corrector


def start():
    stream = sys.stdin.buffer
    # print(stream.read(10))
    # # stream.seek(0)
    img = get_image(stream)

    corrector = Corrector()
    corrector.correct(img)
    # cv2.imshow("asd", img)
    # cv2.waitKey()

    success, encoded_image = cv2.imencode('.jpg', img)
    out = encoded_image.tostring()
    print(out[:10])
    sys.stdout.buffer.write(out)
    # todo work on next step


if __name__ == '__main__':
    start()
