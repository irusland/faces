import threading
import time

import cv2
import numpy
from numpy import dot
import dlib

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")


class TooManyFaces(Exception):
    pass


class NoFaces(BaseException):
    pass


class Corrector:
    anchor_landmarks = None
    ref_color = None

    def warp_image(self, image, operator_matrix):
        image_shape = image.shape
        output_image = numpy.zeros(image_shape, dtype=image.dtype)
        cv2.warpAffine(image,
                       operator_matrix[:2],
                       (image_shape[1], image_shape[0]),
                       dst=output_image,
                       borderMode=cv2.BORDER_REPLICATE,
                       flags=cv2.WARP_INVERSE_MAP)
        return output_image

    def get_translation_operator_matrix(self, points1, points2):
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

    def get_landmarks(self, image):
        rectangles = detector(image, 1)

        if len(rectangles) > 1:
            raise TooManyFaces
        if len(rectangles) == 0:
            raise NoFaces

        array = [[p.x, p.y] for p in predictor(image, rectangles[0]).parts()]
        return numpy.array(array)

    def get_eyes_landmarks(self, face_landmarks, eye_ranges):
        eyes = None
        for start, stop in eye_ranges:
            selected = face_landmarks[start:stop, :]
            if eyes is None:
                eyes = selected
            else:
                eyes = numpy.vstack((eyes, selected))
        return eyes

    def correct(self, image):

        try:
            landmarks = self.get_landmarks(image)
        except NoFaces:
            print("Warning: No faces in image {}")
            raise
        except TooManyFaces:
            print("Warning: Too many faces in image {}")
            raise

        # If this is the first image, make it the reference.
        if self.anchor_landmarks is None:
            self.anchor_landmarks = landmarks
            print('reference set')
            time.sleep(2)

        operator_matrix = self.get_translation_operator_matrix(
            self.anchor_landmarks, landmarks)

        mask = numpy.zeros(image.shape[:2], dtype=numpy.float64)
        cv2.fillConvexPoly(mask, cv2.convexHull(landmarks), 1)
        mask = mask.astype(numpy.bool)

        masked_image = numpy.zeros_like(image)
        masked_image[mask] = image[mask]
        color = ((numpy.sum(masked_image, axis=(0, 1)) /
                  numpy.sum(mask, axis=(0, 1))))
        if self.ref_color is None:
            self.ref_color = color
        image = image * self.ref_color / color
        # cv2.imshow("masked", masked_image)

        for (x, y) in landmarks:
            cv2.circle(image, (x, y), 3, (0, 0, 255), -1)
        # Translate/rotate/scale the image to fit over the reference image.
        warped = self.warp_image(image, operator_matrix)

        # Write the file to disk.
        # cv2.imwrite(os.path.join(OUT_PATH, fname), warped)

        # cv2.imshow("Frame", warped)

        # if anchor_landmarks is not None:
        #     cv2.imwrite('img.png', frame)
        #     print(operator_matrix)
        #     exit(0)

        # key = cv2.waitKey(1)


if __name__ == '__main__':
    print('Start this script from starter.py')
