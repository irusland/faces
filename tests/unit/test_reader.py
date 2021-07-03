from code.extractors.filemanager import FileManager

import pytest
from pyheif import HeifFile

from tests.utils import path_to_file


@pytest.fixture()
def reader():
    return FileManager()


class TestReader:
    @pytest.mark.parametrize("path", [path_to_file("IMG_4541.HEIC")])
    def test_heif_picture(self, reader, path):
        image: HeifFile = reader.read_heif(path)
        assert image.size == (4032, 3024)
        assert image.mode == "RGB"
