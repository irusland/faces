import os

import dlib
import numpy
from dlib import shape_predictor
from numpy.random import Generator

from definitions import ROOT_DIR


class FacialPredictor:
    def __init__(
        self, model_path: str = "shape_predictor_68_face_landmarks.dat"
    ):
        """
        :param model_path: path for shape predictor
        """
        self._detector = dlib.get_frontal_face_detector()
        model_path = os.path.join(ROOT_DIR, model_path)
        self._predictor: shape_predictor = dlib.shape_predictor(model_path)

    def get_landmarks(self, image: numpy.ndarray) -> Generator[numpy.array]:
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
