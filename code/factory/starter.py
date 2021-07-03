import sys
from code.factory.corrector import Corrector
from code.factory.pipe2image import get_image

import cv2


def start():
    stream = sys.stdin.buffer
    # print(stream.read(10))
    # # stream.seek(0)

    # for line in stream:
    while True:
        data = stream.read()
        if not data:
            break
        img = get_image(data)
        cv2.namedWindow("in", cv2.WINDOW_NORMAL)
        cv2.imshow("in", img)

        corrector = Corrector()
        corrector.correct(img)

        cv2.namedWindow("out", cv2.WINDOW_NORMAL)
        cv2.imshow("out", img)

        cv2.waitKey()

        success, encoded_image = cv2.imencode(".jpg", img)
        out = encoded_image.tostring()
        sys.stdout.buffer.write(out)


if __name__ == "__main__":
    start()
