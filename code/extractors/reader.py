from code.utils import with_performance_profile

import pyheif


class Reader:
    @with_performance_profile
    def read_heif(self, path: str) -> pyheif.HeifFile:
        with open(path, "rb") as file:
            return pyheif.read(file)
