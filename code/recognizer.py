import cv2
import numpy as np
import subprocess
import os


def get_shift(a, b):
    ax, ay = a
    bx, by = b
    dx = bx - ax
    dy = by - ay
    return dx, dy


def distance(a, b):
    dx, dy = get_shift(a, b)
    return (dx ** 2 + dy ** 2) ** 0.5


def find_faces(grey, face_cascade_path, count):
    face_cascade = cv2.CascadeClassifier(face_cascade_path)

    faces = face_cascade.detectMultiScale(
        grey,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(30, 30)
    )

    if len(faces) != count:
        return None
        # raise Exception(f'More then {count} faces found')
    return faces[:count]


def get_center(bodyparts):
    for x, y, w, h in bodyparts:
        yield x + w // 2, y + h // 2


def find_eyes(grey, eye_cascade_path):
    eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
    eyes = eye_cascade.detectMultiScale(
        grey,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(30, 30)
    )
    if len(eyes) != 2:
        return None
        # raise Exception('More than two eyes found!')
    return eyes


def compress(image, compression):
    (height, width, _) = image.shape
    dsize = 1 - compression
    return cv2.resize(image, (int(width * dsize), int(height * dsize)))


def resize(root, name, ext):
    face_cascade_path = "face.xml"
    eye_cascade_path = "eye.xml"

    eyedist_precentage = 10

    path = os.path.join(root, name)
    subprocess.call(f'mogrify '
                    f'-format jpeg '
                    f'{path}.{ext} ',
                    shell=True)
    image = cv2.imread(f'{path}.jpeg')
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # image = compress(image, 0.3)
    (height, width, _) = image.shape

    image_center_point = (width // 2, height // 2)

    face = find_faces(grey, face_cascade_path, 1)
    if face is None:
        return
    nose_point = list(get_center(face))[0]

    eyes = find_eyes(grey, eye_cascade_path)
    if eyes is None:
        return
    eyeballs = list(get_center(eyes))
    eyes_distance = distance(eyeballs[0], eyeballs[1])

    dx, dy = get_shift(nose_point, image_center_point)
    scale = (width * eyedist_precentage) / (100 * eyes_distance)

    m = np.float32([[1, 0, dx], [0, 1, dy]])
    image = cv2.warpAffine(image, m, (width, height))
    m = cv2.getRotationMatrix2D((width / 2, height / 2), 0, scale)
    image = cv2.warpAffine(image, m, (width, height))

    print(dx, dy, scale)
    # subprocess.call(f'convert {image_dir}/{image_name}.HEIC '
    #                 f'-gravity center '
    #                 f'-page {width * scale}x{height * scale}+{dx}+{dy} '
    #                 f'-background none '
    #                 # f'-flatten '
    #                 f'-gravity center '
    #                 # f'-page {width * scale}x{height * scale}+0+0 '
    #
    #                 # f'+repage '
    #                 f'{image_dir}/{image_name}_edited.HEIC',
    #                 shell=True)

    cv2.imwrite(f'{path}.jpeg', image)

    # cv2.imshow('face', image)
    # cv2.waitKey(10000) -


def main():
    redo = False

    images_paths = []
    dirlist = [x for x in os.walk("src/")]
    for root, dirs, files in dirlist:
        for file in files:
            if file.endswith(".HEIC") or file.endswith('.JPG'):
                name, ext = file.split('.')
                if f'{name}_edited.{ext}' in files and not redo:
                    continue
                path = os.path.join(root, f'{name}.{ext}')
                images_paths.append((root, name, ext, path))
                print(path)
                # resize(root, name, ext)


if __name__ == '__main__':
    main()
