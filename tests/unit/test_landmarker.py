import os
from backend.extractors.landmarker import FacialPredictor
from typing import Tuple

import numpy as np
import pytest

from definitions import MODELS_DIR
from tests.utils import path_to_file


@pytest.fixture()
def single_face_image() -> np.ndarray:
    with open(path_to_file("face.numpy.ndarray"), "rb") as f:
        data = np.load(f)
        return data


PREDICTORS = {
    68: "shape_predictor_68_face_landmarks.dat",
    5: "shape_predictor_5_face_landmarks.dat",
}


@pytest.fixture(params=[68, 5])
def model(request):
    i = request.param
    return i, PREDICTORS[i]


@pytest.fixture()
def predictor_fixture(model: Tuple[int, str]) -> Tuple[int, FacialPredictor]:
    count, file = model
    model_path = os.path.join(MODELS_DIR, file)
    return count, FacialPredictor(model_path)


class TestFacialPredictor:
    def test_yields_single_face(
        self, predictor_fixture: Tuple[int, FacialPredictor], single_face_image
    ):
        _, predictor = predictor_fixture
        marked_faces = list(predictor.get_landmarks(single_face_image))
        assert len(marked_faces) == 1

    def test_has_all_landmarks(
        self, predictor_fixture: Tuple[int, FacialPredictor], single_face_image
    ):
        expected_count, predictor = predictor_fixture
        for face_landmarks in predictor.get_landmarks(single_face_image):
            len(face_landmarks)
