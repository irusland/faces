from typing import BinaryIO, Literal, Tuple, Union

class HeifFile:
    def __init__(
        self,
        *,
        size,
        data,
        metadata,
        color_profile,
        has_alpha,
        bit_depth,
        stride
    ):
        self.mode: Union[Literal["RGB"], Literal["RGBA"]] = (
            "RGBA" if has_alpha else "RGB"
        )
        self.size: Tuple[int, int] = size
        self.data: bytes = data
        self.metadata = metadata
        self.color_profile = color_profile
        self.has_alpha = has_alpha
        self.bit_depth = bit_depth
        self.stride = stride

def read(
    fp: BinaryIO, *, apply_transformations=True, convert_hdr_to_8bit=True
) -> HeifFile:
    pass
