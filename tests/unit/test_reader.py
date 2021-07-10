import logging

import pytest
from PIL.Image import Image
from pyheif import HeifFile

from backend.extractors.converter import Converter
from backend.extractors.filemanager import FileManager
from tests.utils import path_to_file

logger = logging.getLogger(__file__)


@pytest.fixture()
def converter():
    return Converter()


@pytest.fixture()
def reader(converter):
    return FileManager(converter)


class TestReader:
    @pytest.mark.parametrize("path", [path_to_file("IMG_4541.HEIC")])
    def test_heif_picture(self, reader, path):
        image: HeifFile = reader.read_heif(path)
        assert image.size == (4032, 3024)
        assert image.mode == "RGB"

    @pytest.mark.parametrize(
        ("path", "size"),
        [
            (path_to_file("IMG_4541.HEIC"), (4032, 3024)),
            (path_to_file("IMG_8800.jpg"), (1280, 960)),
            (path_to_file("IMG_1337.PNG"), (4032, 3024)),
        ],
    )
    def test_file_support(self, reader, path, size):
        image: Image = reader.read_pil_auto(path)
        assert image.size == size
        assert image.mode == "RGB"
