import logging
import os
import sys
from unittest import mock
from scipy.stats import percentileofscore

import numpy
import numpy as np
import pytest
from cv2 import cv2

from backend.container import Container
from backend.extractors.landmarker import str_landmarks_to_np
from backend.extractors.operator import scale
from backend.file.utils import get_file_hash
from backend.processor import process_images, _scale_adjust

logger = logging.getLogger(__file__)


@pytest.fixture()
def log(caplog):
    caplog.set_level(logging.DEBUG)
    return caplog


class TestProcessing:
    def test_processing(self, container: Container, test_redis, log):
        container.wire(modules=[sys.modules[__name__]])
        db = container.database()
        converter = container.converter()
        predictor = container.predictor()
        reader = container.file_manager()
        reference = container.config.image_reference_path()
        pil_reference = reader.read_pil_auto(reference)
        reference_hash = get_file_hash(reference)
        np_image = converter.pil_image_to_numpy_array(pil_reference)
        np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
        reference_landmarks = predictor.get_landmarks(np_image)
        assert len(reference_landmarks) == 1, 'inconclusive test'
        max_pixel_distance = 10


        process_images()


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
