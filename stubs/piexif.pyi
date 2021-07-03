from typing import Dict, Literal, TypeVar

ExifDict = Dict[str, str]

def dump(exif_dict: ExifDict): ...

class ImageIFD:
    Artist: Literal["Artist"]
