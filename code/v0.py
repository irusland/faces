import cv2
import numpy as np
import time
import subprocess


def get_shift(a, b):
    ax, ay = a
    bx, by = b
    dx = bx - ax
    dy = by - ay
    return dx, dy


def distance(a, b):
    dx, dy = get_shift(a, b)
    return (dx ** 2 + dy ** 2) ** 0.5


def find_face_center_point(grey, face_cascade_path):
    face_cascade = cv2.CascadeClassifier(face_cascade_path)

    faces = face_cascade.detectMultiScale(
        grey,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(30, 30)
    )

    if len(faces) != 1:
        raise Exception('More then one face found')

    (x, y, w, h) = faces[0]
    return x + w // 2, y + h // 2


def find_eyes_center_points(grey, eye_cascade_path):
    eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
    eyes = eye_cascade.detectMultiScale(
        grey,
        scaleFactor=4,
        minNeighbors=5,
        minSize=(30, 30)
    )
    if len(eyes) != 2:
        raise Exception('More than two eyes found!')

    for x, y, w, h in eyes:
        yield (x + w // 2, y + h // 2)


def main():
    a = time.perf_counter()

    image_path = 'src/test.png'
    face_cascade_path = "face.xml"
    eye_cascade_path = "eye.xml"

    dsize = 1
    # dsize = 0.6
    eyedist_precentage = 10

    subprocess.call('mogrify -format jpg src/IMG_0334.heic',
                    shell=True)

    image = cv2.imread(image_path)
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    (height, width, _) = image.shape
    image = cv2.resize(image, (int(width * dsize), int(height * dsize)))
    (height, width, _) = image.shape

    image_center_point = (width // 2, height // 2)

    # for (x, y, w, h) in faces:
    #     nose_point = (x + w // 2, y + h // 2)
    #     cv2.rectangle(image, (x, y), (x+w, y+h), (128, 128, 128), 2)
    #     cv2.drawMarker(image, nose_point, color=(0, 0, 255))
    #     cv2.drawMarker(image, image_center_point, color=(0, 255, 0))
    #     cv2.arrowedLine(image,
    #                     image_center_point,
    #                     nose_point,
    #                     color=(0, 255, 128))

    # for (x, y, w, h) in eyes:
    #     curr_eye = (x + w // 2, y + h // 2)
    #     cv2.drawMarker(image, curr_eye, color=(255, 255, 255))
    #     if prev_eye is not None:
    #         cv2.line(image,
    #                  prev_eye,
    #                  curr_eye,
    #                  color=(255, 255, 255))
    #
    #         dist = distance(prev_eye, curr_eye, width)
    #         font = cv2.FONT_HERSHEY_SIMPLEX
    #         cv2.putText(image,
    #                     f'{int(dist / width * 100)}%',
    #                     prev_eye,
    #                     font,
    #                     1,
    #                     (255, 255, 255),
    #                     1,
    #                     cv2.LINE_AA)

    # cv2.drawMarker(image, image_center_point, color=(255, 0, 0),
    #                markerSize=width)

    nose_point = find_face_center_point(grey, face_cascade_path)

    eyes = find_eyes_center_points(grey, eye_cascade_path)
    eyes = list(eyes)
    eyes_distance = distance(eyes[0], eyes[1])

    dx, dy = get_shift(nose_point, image_center_point)
    m = np.float32([[1, 0, dx], [0, 1, dy]])
    image = cv2.warpAffine(image, m, (width, height))

    scale = (width * eyedist_precentage) / (100 * eyes_distance)
    m = cv2.getRotationMatrix2D((width / 2, height / 2), 0, scale)
    image = cv2.warpAffine(image, m, (width, height))

    cv2.imwrite("src/edited.png", image)

    cv2.imshow('face', image)
    cv2.waitKey(10000)


if __name__ == '__main__':
    main()
