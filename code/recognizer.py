import cv2
import numpy as np
import subprocess
import os

from definitions import ROOT_DIR, CODE_DIR, PHOTOS_SRC_TEST_DIR, \
    PHOTOS_RES_TEST_DIR


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
        scaleFactor=1.4,
        minNeighbors=5,
        minSize=(30, 30)
    )

    if len(faces) != count:
        raise Exception(f'More then {count} faces found')
    return faces[:count]


def get_center(bodyparts):
    for x, y, w, h in bodyparts:
        yield x + w // 2, y + h // 2


def get_part_center(x, y, w, h):
    return x + w // 2, y + h // 2


def find_eyes(grey, eye_cascade_path):
    eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
    eyes = eye_cascade.detectMultiScale(
        grey,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(30, 30)
    )
    if len(eyes) != 2:
        raise Exception('More than two eyes found!', eyes)
    return eyes


def compress(image, compression):
    height, width = image.shape
    dsize = 1 - compression
    return cv2.resize(image, (int(width * dsize), int(height * dsize)))


def get_translation(root, name, ext):
    face_cascade_path = os.path.join(CODE_DIR, 'face.xml')
    eye_cascade_path = os.path.join(CODE_DIR, 'eye.xml')

    eyedist_precentage = 10

    path = os.path.join(root, name)
    image = cv2.imread(f'{path}.jpeg')
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # image = compress(image, 0.5)
    height, width, _ = image.shape

    face_eye_center_x, cy = (width // 2, height // 2)
    image_center_point = (face_eye_center_x, cy)

    # image = cv2.medianBlur(image, 5)

    face = find_faces(grey, face_cascade_path, 1)
    if face is None:
        print('no faces found')
        return
    nose_point = list(get_center(face))[0]

    eyes = find_eyes(grey, eye_cascade_path)
    if eyes is None:
        print('no eyes found')
        return
    eyeballs = list(get_center(eyes))
    eyes_distance = distance(eyeballs[0], eyeballs[1])

    for x, y, w, h in eyes:
        # face_eye_center_x, face_eye_center_y = get_part_center(x, y, w, h)
        eye = image[y:y + h, x:x + w]

        height, width = eye.shape[:2]
        eye = eye[25:height, 0:width]

        img = eye
        gimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, gimg = cv2.threshold(gimg, 88, 255, cv2.THRESH_BINARY)
        gimg = cv2.erode(gimg, None, iterations=4)
        gimg = cv2.dilate(gimg, None, iterations=16)
        gimg = cv2.medianBlur(gimg, 5)

        detector_params = cv2.SimpleBlobDetector_Params()
        detector_params.filterByArea = True
        detector_params.maxArea = 1500
        detector = cv2.SimpleBlobDetector_create(detector_params)
        keypoints = detector.detect(gimg)
        print(keypoints)
        cv2.imshow(f'parsed {keypoints}', gimg)
        cimg = img
        cv2.drawKeypoints(cimg, keypoints, cimg, (0, 255, 0),
                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imshow(f'img {keypoints}', img)
        cv2.imshow(f'final {keypoints}', cimg)

        cimg = image
        for kp in keypoints:
            kp: cv2.KeyPoint = kp
            eye_center_x, eye_center_y = kp.pt
            eye_center_x = int(eye_center_x)
            eye_center_y = int(eye_center_y)
            r = int(kp.size)

            center_on_face = (x + eye_center_x,
                              25 + y + eye_center_y)

            cv2.circle(cimg, center_on_face, r, (0, 255, 0), 2)
            cv2.circle(cimg, center_on_face, 2, (0, 0, 255), 3)

            center_on_eye = (eye_center_x, eye_center_y)

            cv2.circle(eye, center_on_eye, r, (0, 255, 0), 2)
            cv2.circle(eye, center_on_eye, 2, (0, 0, 255), 3)

        # cv2.imshow(f'detected circles {(eye_center_x, eye_center_y)}', cimg)
        cv2.imshow(f'eye {(eye_center_x, eye_center_y)}', eye)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    dx, dy = get_shift(nose_point, image_center_point)
    scale = (width * eyedist_precentage) / (100 * eyes_distance)

    # m = np.float32([[1, 0, dx], [0, 1, dy]])
    # image = cv2.warpAffine(image, m, (width, height))
    #
    # m = cv2.getRotationMatrix2D((width / 2, height / 2), 0, scale)
    # image = cv2.warpAffine(image, m, (width, height))

    cv2.rectangle(image, eyes[0], (255, 0, 0), 5)
    cv2.rectangle(image, eyes[1], (255, 0, 0), 5)
    cv2.rectangle(image, face, (255, 0, 0), 5)

    cv2.imshow('centered', image)
    cv2.waitKey(0)

    return face_eye_center_x, cy, dx, dy, scale
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

    # return image


def main():
    redo = False

    images_paths = []
    dirlist = [x for x in os.walk(PHOTOS_SRC_TEST_DIR)]
    for root, dirs, files in dirlist:
        for file in files:
            if file.endswith('.HEIC') or file.endswith('.JPG'):
                name, ext = file.split('.')
                if f'{name}_edited.{ext}' in files and not redo:
                    continue
                src_path = os.path.join(root, f'{name}.{ext}')
                images_paths.append((root, name, ext, src_path))
                print('processing ', src_path)

                # subprocess.call(f'mogrify '
                #                 f'-format jpeg '
                #                 f'{src_path}',
                #                 shell=True)

                cx, cy, dx, dy, scale = get_translation(root, name, ext)
                print('translation ', dx, dy, scale)

                res_path = os.path.join(PHOTOS_RES_TEST_DIR, f'{name}.{ext}')
                # subprocess.call(f'convert {src_path} '
                #                 f'-distort SRT "0,0 1 0 {dx},{dy}" '
                #                 f'-distort SRT "{scale} 0" '
                #                 f'-distort SRT "0" '
                #                 f'-colorspace sRGB '
                #                 f'{res_path}', shell=True)
                print('saved ', res_path)


if __name__ == '__main__':
    main()
