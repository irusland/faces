import hashlib
import logging
import sys
from code.utils import with_performance_profile

FORMAT = "[%(filename)15s|%(funcName)15s:%(lineno)4s] %(message)s"
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__file__)


@with_performance_profile
def get_file_hash(path: str) -> str:
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


if __name__ == "__main__":
    print(get_file_hash("/Users/irusland/Desktop/123123123.PNG"))
