import datetime
import hashlib

import exifread

from backend.utils import with_performance_profile


@with_performance_profile
def get_file_hash(path: str) -> str:
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@with_performance_profile
def get_datetime_original(path: str) -> datetime.datetime:
    _format = "%Y:%m:%d %H:%M:%S"
    with open(path, "rb") as fh:
        tags = exifread.process_file(  # type: ignore
            fh, stop_tag="EXIF DateTimeOriginal"
        )
        tag = tags["EXIF DateTimeOriginal"]
        return datetime.datetime.strptime(tag.values, _format)  # type: ignore
