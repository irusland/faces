from code.utils import with_performance_profile

import numpy
from cv2 import cv2
from numpy import dot


@with_performance_profile
def warp_image(image, operator_matrix):
    image_shape = image.shape
    output_image = numpy.zeros(image_shape, dtype=image.dtype)
    cv2.warpAffine(
        image,
        operator_matrix[:2],
        (image_shape[1], image_shape[0]),
        dst=output_image,
        borderMode=cv2.BORDER_REPLICATE,
        flags=cv2.WARP_INVERSE_MAP,
    )
    return output_image


@with_performance_profile
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
    transformation_matrix = numpy.vstack(
        [
            numpy.hstack(
                (scaled_rotation_matrix, numpy.vstack(translation_matrix))
            ),
            numpy.array([0.0, 0.0, 1.0]),
        ]
    )

    return transformation_matrix
