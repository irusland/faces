import argparse
import io
import os

import cv2
import exifread
import numpy
import piexif
import pyheif
from PIL import Image


def processdir(path):
    print(f"{path} directory processing")
    dirlist = [x for x in os.walk(path)]
    for root, dirs, files in dirlist:
        for full_file_name in files:
            processfile(full_file_name)
        for dir in dirs:
            processdir(dir)


def processfile(path):
    print(f"{path} file processing")
    # with tempfile.NamedTemporaryFile(mode="wb") as jpg:
    #     ...
    #     jpg.write(b"Hello World!")
    # ...
    # print
    # jpg.name


def pillow_to_cv2_image(pillow_image):
    return cv2.cvtColor(numpy.array(pillow_image), cv2.COLOR_RGB2BGR)


def rw_exif(meta, filename):
    image = Image.frombytes(
        mode=meta.mode, size=meta.size, data=meta.data
    ).convert("RGB")

    exif_dict = {}
    for metadata in meta.metadata or []:
        if metadata["type"] == "Exif":
            stream = io.BytesIO(metadata["data"][6:])
            exif_dict = exifread.process_file(stream)
            for k, v in exif_dict.items():
                print("{:30s} {:3s}".format(k, str(v)))
    # process im and exif_dict...
    w, h = image.size
    exif_dict[piexif.ImageIFD.Artist] = "Rusland"

    exif_bytes = piexif.dump(exif_dict)
    print("---------------")
    for k, v in exif_dict.items():
        print("{:30s} {:3s}".format(str(k), str(v)))

    image.save("save.heic", format="heic", exif=exif_bytes)


def read_meta(path: str):
    with open(path, "rb") as file:
        return pyheif.read(file)


def main():
    parser = argparse.ArgumentParser(description="Set photo landmarks")
    # TODO stdin
    parser.add_argument(
        "input",
        metavar="input",
        type=str,
        nargs="+",
        help="Input path to process",
    )

    args = parser.parse_args()

    for path in args.input:
        if os.path.isdir(path):
            processdir(path)
        else:
            processfile(path)


if __name__ == "__main__":
    file = "/Users/irusland/Desktop/UrFU/python/faces/src_test/IMG_0518.HEIC"
    meta = read_meta(file)
    rw_exif(meta, file)
    # main()
