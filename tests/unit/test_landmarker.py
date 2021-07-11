import os
from typing import Tuple

import numpy
import numpy as np
import pytest
from scipy.stats import percentileofscore

from backend.extractors.converter import Converter
from backend.extractors.filemanager import FileManager
from backend.extractors.landmarker import FacialPredictor
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


@pytest.fixture()
def converter() -> Converter:
    return Converter()


@pytest.fixture()
def file_manager(converter: Converter) -> FileManager:
    return FileManager(converter)


@pytest.fixture()
def to_test_face_image(
    request, file_manager: FileManager, converter: Converter
):
    pil_image = file_manager.read_pil_auto(request.param)
    return converter.pil_image_to_numpy_array(pil_image)


@pytest.fixture()
def authentic_image(request, file_manager: FileManager, converter: Converter):
    pil_image = file_manager.read_pil_auto(request.param)
    return converter.pil_image_to_numpy_array(pil_image)


class TestMultipleFaces:
    @pytest.mark.parametrize(
        ("to_test_face_image", "authentic_image"),
        [
            (
                path_to_file("bigger_wins_test.PNG"),
                path_to_file("bigger_wins_expected.PNG"),
            ),
            (
                path_to_file("extract_center_test.HEIC"),
                path_to_file("extract_center_expected.HEIC"),
            ),
            (
                path_to_file("small_center_wins_test.jpg"),
                path_to_file("small_center_wins_expected.jpg"),
            ),
        ],
        indirect=True,
    )
    def test_select_main_face(
        self,
        predictor_fixture: Tuple[int, FacialPredictor],
        to_test_face_image: numpy.ndarray,
        authentic_image: numpy.ndarray,
    ):
        max_pixel_distance = 20
        _, predictor = predictor_fixture
        height, width, colors = authentic_image.shape
        mid_point = numpy.array([width / 2, height / 2])

        landmarks = predictor.get_landmarks(to_test_face_image)
        actual = predictor.select_main_face(landmarks, mid_point)

        (expected_face,) = predictor.get_landmarks(authentic_image)
        diff = expected_face - actual
        diff_sm = (np.sqrt(diff * diff)).mean(axis=1)
        score = percentileofscore(diff_sm, max_pixel_distance)
        assert score > 90

    @pytest.mark.parametrize(
        "to_test_face_image",
        [
            path_to_file("no_faces.jpg"),
        ],
        indirect=True,
    )
    def test_no_faces(
        self,
        predictor_fixture: Tuple[int, FacialPredictor],
        to_test_face_image: numpy.ndarray,
    ):
        _, predictor = predictor_fixture
        height, width, colors = to_test_face_image.shape
        mid_point = numpy.array([width / 2, height / 2])

        landmarks = predictor.get_landmarks(to_test_face_image)
        with pytest.raises(RuntimeError):
            predictor.select_main_face(landmarks, mid_point)
