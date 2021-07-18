import logging
import sys

import pytest

from backend.processor import process_images

logger = logging.getLogger(__file__)


@pytest.fixture()
def log(caplog):
    caplog.set_level(logging.DEBUG)
    return caplog


class TestProcessing:
    def test_processing(self, container, test_redis, log):
        container.wire(modules=[sys.modules[__name__]])
        process_images()
