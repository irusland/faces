from typing import BinaryIO, Literal, Tuple, Union

class HeifFile:
    def __init__(self):
        self.mode: Union[Literal["RGB"], Literal["RGBA"]]
        self.size: Tuple[int, int]
        self.data: bytes

def read(
    fp: BinaryIO, *, apply_transformations=True, convert_hdr_to_8bit=True
) -> HeifFile:
    pass
