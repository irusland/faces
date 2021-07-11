import pytest

from backend.file.utils import get_file_hash
from tests.utils import path_to_file


class TestGetDatetimeOriginal:
    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            (path_to_file("IMG_1337.PNG"), "f6f9b4220ca8beadb1dcbc39d5ed4ab6"),
            (
                path_to_file("IMG_4541.HEIC"),
                "6ad3596f893f3bd098edf2331edfa201",
            ),
            (path_to_file("IMG_8800.jpg"), "3653511868f7ed37e70701f22e4905e0"),
        ],
    )
    def test_get_hash_by_file(self, path, expected):
        actual1 = get_file_hash(path)
        actual2 = get_file_hash(path)
        assert actual1 == actual2 == expected
