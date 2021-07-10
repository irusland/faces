import pickle
from backend.extractors.converter import Converter

import pytest
from PIL.Image import Image
from pyheif import HeifFile

from tests.utils import path_to_file


@pytest.fixture()
def converter():
    return Converter()


@pytest.fixture()
def image(request):
    with open(path_to_file(request.param), "rb") as f:
        return pickle.load(f)


class TestConverter:
    @pytest.mark.parametrize("image", ["face.heif_file"], indirect=True)
    def test_heif_pil_conversion(self, converter, image: HeifFile):
        pil_image: Image = converter.pyheif_to_pil_image(image)
        assert pil_image.mode == image.mode
        assert pil_image.size == image.size

    @pytest.mark.parametrize("image", ["face.pil_image"], indirect=True)
    def test_pil_np_conversion(self, converter, image: Image):
        array = converter.pil_image_to_numpy_array(image)
        assert array.shape == (*image.size[::-1], 3)
