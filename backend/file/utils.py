import hashlib
import logging

from backend.utils import with_performance_profile

logger = logging.getLogger(__file__)


@with_performance_profile
def get_file_hash(path: str) -> str:
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


if __name__ == "__main__":
    print(
        get_file_hash(
            "/Users/irusland/Downloads/iCloud Photos 3/IMG_4565.HEIC"
        )
    )
    print(
        get_file_hash(
            "/Users/irusland/Downloads/iCloud Photos 4/IMG_4565.HEIC"
        )
    )
    print(get_file_hash("/Users/irusland/Downloads/IMG_4565.HEIC"))
