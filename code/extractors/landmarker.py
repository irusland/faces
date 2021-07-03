from code.utils import with_performance_profile
from typing import Generator

import dlib
import numpy
from dlib import shape_predictor


class FacialPredictor:
    def __init__(self, model_path: str):
        """
        :param model_path: path for shape predictor
        """
        self._detector = dlib.get_frontal_face_detector()
        self._predictor: shape_predictor = dlib.shape_predictor(model_path)

    @with_performance_profile
    def get_landmarks(
        self, image: numpy.ndarray
    ) -> Generator[numpy.ndarray, None, None]:
        """
        Gets face landmarks
        :param image: numpy matrix of image
        :return: for each face an array of dots (x, y pairs)
        """
        rectangles = self._detector(image, 1)
        for face_bounds in rectangles:
            array = [
                [p.x, p.y] for p in self._predictor(image, face_bounds).parts()
            ]
            yield numpy.array(array)
