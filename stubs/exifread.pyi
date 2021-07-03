from typing import Dict

ExifDict = Dict[str, str]

def process_file(stream) -> ExifDict: ...
