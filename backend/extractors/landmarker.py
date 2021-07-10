import base64
import pickle
from typing import List

import dlib
import numpy
from dlib import shape_predictor

from backend.utils import with_performance_profile


class FacialPredictor:
    def __init__(self, model_path: str):
        """
        :param model_path: path for shape predictor
        """
        self._detector = dlib.get_frontal_face_detector()
        self._predictor: shape_predictor = dlib.shape_predictor(model_path)
        self._model_path = model_path

    @with_performance_profile
    def get_landmarks(self, image: numpy.ndarray) -> List[numpy.ndarray]:
        """
        Gets face landmarks
        :param image: numpy matrix of image
        :return: for each face an array of dots (x, y pairs)
        """
        rectangles = dlib.get_frontal_face_detector()(image, 1)
        faces = []
        for face_bounds in rectangles:
            array = [
                [p.x, p.y]
                for p in dlib.shape_predictor(self._model_path)(
                    image, face_bounds
                ).parts()
            ]
            faces.append(numpy.array(array))
        return faces


@with_performance_profile
def np_landmarks_to_bytes(
    arrays: List[numpy.ndarray],
) -> bytes:
    return pickle.dumps(arrays)


@with_performance_profile
def bytes_landmarks_to_np(serialized: bytes) -> List[numpy.ndarray]:
    return pickle.loads(serialized)


@with_performance_profile
def np_landmarks_to_str(
    arrays: List[numpy.ndarray],
) -> str:
    return base64.b64encode(np_landmarks_to_bytes(arrays))  # type: ignore


@with_performance_profile
def str_landmarks_to_np(serialized: str) -> List[numpy.ndarray]:
    return bytes_landmarks_to_np(base64.b64decode(serialized))
