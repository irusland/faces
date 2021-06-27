import os
from code.extractors.landmarker import FacialPredictor

import numpy as np
import pytest

from definitions import MODELS_DIR
from tests.utils import path_to_file


@pytest.fixture()
def single_face_image() -> np.ndarray:
    with open(path_to_file("face.numpy.ndarray"), "rb") as f:
        data = np.load(f)
        return data


@pytest.fixture()
def predictor():
    model_file = "shape_predictor_68_face_landmarks.dat"
    model_path = os.path.join(MODELS_DIR, model_file)
    return FacialPredictor(model_path)


class TestFacialPredictor:
    def test_yields_all_faces(
        self, predictor: FacialPredictor, single_face_image
    ):
        marked_faces = list(predictor.get_landmarks(single_face_image))
        assert len(marked_faces) == 1
