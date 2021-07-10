import numpy.testing
import pytest

from backend.extractors.landmarker import (
    bytes_landmarks_to_np,
    np_landmarks_to_bytes,
)


class TestConversion:
    @pytest.mark.parametrize(
        "landmarks",
        [
            numpy.array(
                [
                    [[1, 2], [1, 2], [1, 2], [1, 2], [1, 2]],
                    [[3, 4], [1, 2], [1, 5]],
                ],
                dtype=object,
            ),
            numpy.array(
                [
                    [[1, 2], [1, 2], [1, 2], [1, 2], [1, 2]],
                    [[1, 2], [1, 2], [1, 2], [1, 2], [1, 2]],
                    [[3, 4], [1, 2], [1, 5]],
                ],
                dtype=object,
            ),
            numpy.array(
                [
                    [],
                    [[1, 2]],
                ],
                dtype=object,
            ),
            numpy.array(
                [
                    [[1, 2], [1, 2], [1, 2], [1, 2], [1, 2]],
                ]
            ),
            numpy.array([[]]),
            numpy.array([]),
        ],
    )
    def test_landmarks_serialization(self, landmarks):
        expected = iter(landmarks)
        serialized = np_landmarks_to_bytes(expected)
        actual = bytes_landmarks_to_np(serialized)
        actual_list, expected_list = list(actual), list(expected)
        assert len(actual_list) == len(expected_list)
        for array_actual, array_expected in zip(actual_list, expected_list):
            numpy.testing.assert_array_equal(array_actual, array_expected)
