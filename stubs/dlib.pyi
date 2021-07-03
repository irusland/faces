from typing import Generic, Iterator, TypeVar

class Dot:
    x: float
    y: float

class shape_predictor:
    def __init__(self, model_path: str) -> None: ...
    def parts(self) -> Iterator[Dot]: ...
    def __call__(self, *args, **kwargs): ...

class default_fhog_feature_extractor: ...
class _6u: ...

TSize = TypeVar("TSize")

class pyramid_down(Generic[TSize]): ...

TOrientation = TypeVar("TOrientation")
TExtractor = TypeVar("TExtractor")

class scan_fhog_pyramid(Generic[TOrientation, TExtractor]): ...

TScan = TypeVar("TScan")

class object_detector(Generic[TScan]):
    def __call__(self, *args, **kwargs): ...

def get_frontal_face_detector() -> object_detector[
    scan_fhog_pyramid[pyramid_down[_6u], default_fhog_feature_extractor]
]: ...
