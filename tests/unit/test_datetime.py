from datetime import datetime

import pytest

from backend.file.utils import get_datetime_original
from tests.utils import path_to_file


class TestGetDatetimeOriginal:
    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            (path_to_file("IMG_4541.HEIC"), datetime(2021, 7, 2, 22, 38, 24)),
            (path_to_file("IMG_8800.jpg"), datetime(2018, 11, 26, 23, 43, 48)),
        ],
    )
    def test_get_time(self, path, expected):
        actual = get_datetime_original(path)
        assert actual == expected

    @pytest.mark.parametrize(
        "path",
        [
            path_to_file("IMG_1337.PNG"),
        ],
    )
    def test_no_time(self, path):
        with pytest.raises(Exception):
            get_datetime_original(path)
