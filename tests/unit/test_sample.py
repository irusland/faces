import pytest

from code.factory.corrector import TooManyFaces


@pytest.fixture()
def data():
    return {1: 2}


class TestSample:
    def test_fail(self, data):
        assert data == {1: 2}

    def test_class(self):
        tmf = TooManyFaces()
        assert isinstance(tmf, Exception)
