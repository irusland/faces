import datetime
import fnmatch
import hashlib
import logging
import os
import re
from typing import Optional

import exifread

from backend.utils import with_performance_profile

logger = logging.getLogger(__file__)


@with_performance_profile
def get_file_hash(path: str) -> str:
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@with_performance_profile
def get_datetime_original(path: str) -> Optional[datetime.datetime]:
    _format = "%Y:%m:%d %H:%M:%S"
    _keys = ["EXIF DateTimeOriginal", "EXIF SubSecTimeOriginal"]
    with open(path, "rb") as fh:
        tags = exifread.process_file(  # type: ignore
            fh, stop_tag="EXIF DateTimeOriginal"
        )

        for key in _keys:
            if tag := tags.get(key):
                return datetime.datetime.strptime(
                    tag.values, _format  # type: ignore
                )
        return None


def get_paths_to_process(source_dir: str):
    includes = ["*.jpg", "*.png", "*.heic", "*.jpeg", "*.heif"]
    include_pattern = r"|".join([fnmatch.translate(x) for x in includes])
    files = set()
    for (dirpath, dirnames, filenames) in os.walk(source_dir):
        files.update(
            {
                os.path.join(source_dir, filename)
                for filename in filenames
                if re.match(include_pattern, filename, flags=re.IGNORECASE)
            }
        )
    return files
