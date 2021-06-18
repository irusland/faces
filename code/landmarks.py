import os
import threading
import time

from cv2 import cv2
import numpy
from numpy import dot
import dlib

from definitions import ROOT_DIR

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

detector = dlib.get_frontal_face_detector()
model_path = os.path.join(ROOT_DIR, "shape_predictor_68_face_landmarks.dat")
predictor = dlib.shape_predictor(model_path)


class TooManyFaces(Exception):
    pass


class NoFaces(BaseException):
    pass


def warp_image(image, operator_matrix):
    image_shape = image.shape
    output_image = numpy.zeros(image_shape, dtype=image.dtype)
    cv2.warpAffine(image,
                   operator_matrix[:2],
                   (image_shape[1], image_shape[0]),
                   dst=output_image,
                   borderMode=cv2.BORDER_REPLICATE,
                   flags=cv2.WARP_INVERSE_MAP)
    return output_image


def get_translation_operator_matrix(points1, points2):
    points1 = points1.astype(numpy.float64)
    points2 = points2.astype(numpy.float64)

    # Compute middle face point
    c1 = numpy.mean(points1, axis=0)
    c2 = numpy.mean(points2, axis=0)

    # Translate to origin
    points1 -= c1
    points2 -= c2

    # Compute scale (Point distribution)
    s1 = numpy.std(points1[:-1])
    s2 = numpy.std(points2[:-1])

    # Normalize points
    points1 /= s1
    points2 /= s2

    # Singular Value Decomposition
    # https://towardsdatascience.com/understanding-singular-value-decomposition-and-its-application-in-data-science-388a54be95d
    U, S, Vt = numpy.linalg.svd(numpy.dot(points1.T, points2))

    # todo apply distortion
    # U.dot(numpy.diag(S)).dot(Vt)

    # cosa -sina
    # sina cosa
    rotation_matrix = U.dot(Vt).T
    scaled_rotation_matrix = dot(abs(s2 / s1), rotation_matrix)

    # apply translation after rotation!
    translation_matrix = c2.T - dot(scaled_rotation_matrix, c1.T)

    # cosa -sina dx
    # sina cosa  dy
    # 0    0     1
    transformation_matrix = numpy.vstack([
        numpy.hstack((scaled_rotation_matrix, numpy.vstack(translation_matrix))),
        numpy.array([0., 0., 1.])
    ])

    return transformation_matrix


def get_landmarks(image):
    rectangles = detector(image, 1)

    if len(rectangles) > 1:
        raise TooManyFaces
    if len(rectangles) == 0:
        raise NoFaces

    array = [[p.x, p.y] for p in predictor(image, rectangles[0]).parts()]
    return numpy.array(array)


def get_eyes_landmarks(face_landmarks, eye_ranges):
    eyes = None
    for start, stop in eye_ranges:
        selected = face_landmarks[start:stop, :]
        if eyes is None:
            eyes = selected
        else:
            eyes = numpy.vstack((eyes, selected))
    return eyes


def main():
    anchor_landmarks = None
    ref_color = None
    while True:
        _, frame = cap.read()
        # frame = cv2.imread('dlib-landmark-mean.png')
        image = frame
        # image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # cv2.imshow("asd", frame)

        # Compute landmark features for the face in the image.
        try:
            landmarks = get_landmarks(image)
            from_68 = ((36, 42), (42, 48))
            from_5 = ((0, 2), (2, 4))
            # landmarks = get_eyes_landmarks(landmarks, from_68)
        except NoFaces:
            print("Warning: No faces in image {}")
            continue
        except TooManyFaces:
            print("Warning: Too many faces in image {}")
            continue

        # If this is the first image, make it the reference.
        if anchor_landmarks is None:
            anchor_landmarks = landmarks
            print('reference set')
            time.sleep(2)

        operator_matrix = get_translation_operator_matrix(anchor_landmarks, landmarks)

        mask = numpy.zeros(image.shape[:2], dtype=numpy.float64)
        cv2.fillConvexPoly(mask, cv2.convexHull(landmarks), 1)
        mask = mask.astype(numpy.bool)

        masked_image = numpy.zeros_like(image)
        masked_image[mask] = image[mask]
        # color = ((numpy.sum(masked_image, axis=(0, 1)) /
        #           numpy.sum(mask, axis=(0, 1))))
        # if ref_color is None:
        #     ref_color = color
        # image = image * ref_color / color
        cv2.imshow("masked", masked_image)

        for (x, y) in landmarks:
            cv2.circle(image, (x, y), 3, (0, 0, 255), -1)
        # Translate/rotate/scale the image to fit over the reference image.
        warped = warp_image(image, operator_matrix)

        # Write the file to disk.
        # cv2.imwrite(os.path.join(OUT_PATH, fname), warped)

        cv2.imshow("Frame", warped)

        # if anchor_landmarks is not None:
        #     cv2.imwrite('img.png', frame)
        #     print(operator_matrix)
        #     exit(0)

        key = cv2.waitKey(1)
        if key == 27:
            break


if __name__ == '__main__':
    main()
