import os

from definitions import ROOT_DIR

DATA_DIR = os.path.join("tests", "data")
TEST_DATA_DIR = os.path.join(ROOT_DIR, DATA_DIR)


def path_to_file(filename: str) -> str:
    return os.path.join(TEST_DATA_DIR, filename)
