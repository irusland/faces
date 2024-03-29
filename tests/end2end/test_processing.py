import logging
import os

import numpy as np
import pytest
from cv2 import cv2
from scipy.stats import percentileofscore

from backend.container import Container
from backend.extractors.landmarker import str_landmarks_to_np
from backend.processor import process_images

logger = logging.getLogger(__file__)


@pytest.fixture()
def log(caplog):
    caplog.set_level(logging.DEBUG)
    return caplog


@pytest.fixture()
def prepare_dirs(container: Container):
    os.makedirs(container.result_settings().path, exist_ok=True)


class TestProcessing:
    def test_processing(
        self, container: Container, prepare_dirs, test_redis, log
    ):
        from backend import processor

        container.wire(modules=[processor])
        db = container.database()
        converter = container.converter()
        predictor = container.predictor()
        reader = container.file_manager()
        reference = container.reference_settings().path
        pil_reference = reader.read_pil_auto(reference)
        np_image = converter.pil_image_to_numpy_array(pil_reference)
        np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
        reference_landmarks = predictor.get_landmarks(np_image)
        assert len(reference_landmarks) == 1, "inconclusive test"
        max_pixel_distance = 10

        assert process_images()

        infos = db.get_all_infos()
        assert infos
        for info in infos:
            hash = info.image_hash
            data = db.get_landmarks(hash)
            assert data
            landmarks = str_landmarks_to_np(data.landmarks)
            assert landmarks

            assert os.path.isfile(info.origin_path)
            assert os.path.isfile(info.save_path)

            pil_actual = reader.read_pil_auto(info.save_path)
            np_image = converter.pil_image_to_numpy_array(pil_actual)
            np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
            middle_point = converter.pil_image_center(pil_actual)
            main_landmarks = predictor.select_main_face(
                predictor.get_landmarks(np_image), middle_point
            )
            actual_landmarks = main_landmarks
            diff = reference_landmarks - actual_landmarks
            diff_sm = (np.abs(diff)).mean(axis=1)
            score = percentileofscore(diff_sm, max_pixel_distance)
            assert score > 95
