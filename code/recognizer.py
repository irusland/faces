import os
import pickle
import subprocess
import time

import cv2

from definitions import CACHE, CODE_DIR, PHOTOS_RES_DIR, PHOTOS_RES_TEST_DIR


class Face:
    def __init__(self, path, eye1, eye2, width, height):
        self.path = path
        self.width, self.height = width, height
        self.eye1, self.eye2 = eye1, eye2
        self.eye_distance = distance(eye1, eye2)
        lx, ly = eye1
        rx, ry = eye2
        self.middle_point = ((rx + lx) // 2, (ry + ly) // 2)


def get_shift(p1, p2):
    ax, ay = p1
    bx, by = p2
    dx = bx - ax
    dy = by - ay
    return dx, dy


def distance(p1, p2):
    dx, dy = get_shift(p1, p2)
    return (dx ** 2 + dy ** 2) ** 0.5


def filter_faces(grey, faces):
    sw, sh = grey.shape
    center_x = sw // 2
    center_y = sh // 2

    closest_dist = -1
    closest_face = None

    for face in faces:
        x, y, w, h = face
        grey = cv2.rectangle(grey, (x, y), (x + w, y + h), (255, 0, 0), 5)
        grey = cv2.resize(grey, (800, 400))

        x, y = get_part_center(*face)
        dist = distance((x, y), (center_x, center_y))
        if closest_dist == -1 or dist < closest_dist or closest_face is None:
            closest_dist = dist
            closest_face = face
    return closest_face


def find_1_face(grey, face_cascade_path, count):
    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    faces = face_cascade.detectMultiScale(
        grey, scaleFactor=1.4, minNeighbors=5, minSize=(30, 30)
    )
    face = filter_faces(grey, faces)
    if face is None:
        raise Exception("No face found")
    return faces[:count]


def get_center(bodyparts):
    for x, y, w, h in bodyparts:
        yield x + w // 2, y + h // 2


def get_part_center(x, y, w, h):
    return x + w // 2, y + h // 2


def filter_eyes(grey, eyes):
    sw, sh = grey.shape
    for eye in eyes:
        x, y = get_part_center(*eye)
        if y < sh // 2:
            yield eye


def find_2_eyes(grey, eye_cascade_path):
    eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
    eyes = eye_cascade.detectMultiScale(
        grey, scaleFactor=1.2, minNeighbors=20, minSize=(30, 30)
    )
    eyes = list(filter_eyes(grey, eyes))
    if len(eyes) != 2:
        image = grey
        for x, y, w, h in eyes:
            image = cv2.rectangle(grey, (x, y), (x + w, y + h), (0, 0, 255), 5)
        image = cv2.resize(image, (800, 400))
        cv2.imshow(f"{len(eyes)}", image)
        raise Exception("Not two eyes found!", eyes)
    return eyes


def find_eyes_centers(abs_image_path):
    face_cascade_path = os.path.join(CODE_DIR, "face.xml")
    eye_cascade_path = os.path.join(CODE_DIR, "eye.xml")

    image = cv2.imread(abs_image_path)
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    grey = cv2.medianBlur(grey, 5)
    height, width, _ = image.shape

    # img_center_x, img_center_y = (width // 2, height // 2)
    # image_center_point = (img_center_x, img_center_y)

    try:
        faces = find_1_face(grey, face_cascade_path, 1)
    except Exception:
        cv2.imwrite(f"{abs_image_path}.fail.jpeg", grey)
        raise

    face = faces[0]
    # face_center = get_part_center(*face)
    fx, fy, fw, fh = face
    face_img = grey[fy : fy + fh, fx : fx + fw]

    try:
        eyes = find_2_eyes(face_img, eye_cascade_path)
    except Exception:
        cv2.imwrite(f"{abs_image_path}.fail.jpeg", grey)
        raise

    eye_centers = []
    # each eye processing
    for x, y, w, h in eyes:
        # eye_img = face_img[y: y + h, x: x + w]
        eye_centers.append((fx + (x + w // 2), fy + (y + h // 2)))
    return eye_centers


def main():
    REDO = False
    SRC_DIR = "/Users/irusland/Downloads/iCloudPhotos"
    RES_DIR = PHOTOS_RES_DIR

    COUNTER = 0

    faces = {}
    try:
        with open(CACHE, "rb") as f:
            faces = pickle.load(f)
    except Exception:
        print("No cache found")
    else:
        print(f"{len(faces)} processed images found")

    dirlist = [x for x in os.walk(SRC_DIR)]
    for root, dirs, files in dirlist:
        for full_file_name in files:
            COUNTER += 1
            if (
                not full_file_name.endswith(".HEIC")
                and not full_file_name.endswith(".JPG")
                and not full_file_name.endswith(".jpg")
            ):
                continue
            file_name, file_ext = full_file_name.split(".")
            abs_file_path = os.path.join(root, f"{file_name}.{file_ext}")

            if (
                os.path.exists(
                    os.path.join(PHOTOS_RES_TEST_DIR, full_file_name)
                )
                or abs_file_path in faces
            ) and not REDO:
                continue

            abs_converted_path = os.path.join(root, f"{file_name}.jpeg")

            print(
                f"step {COUNTER}/{len(files)}" f" processing ", abs_file_path
            )

            subprocess.call(
                f"mogrify " f"-format jpeg " f"{abs_file_path}", shell=True
            )

            try:
                eye_1_center, eye_2_center = find_eyes_centers(
                    abs_converted_path
                )
                image = cv2.imread(abs_converted_path)
                height, width, _ = image.shape

                face = Face(
                    abs_file_path, eye_1_center, eye_2_center, width, height
                )
                faces[abs_file_path] = face

                with open(CACHE, "wb") as f:
                    pickle.dump(faces, f)

            except Exception as e:
                print(e.args)
                continue

            finally:
                os.remove(abs_converted_path)

    mx, my = 0, 0
    md = 0
    for face in faces.values():
        x, y = face.middle_point
        mx += x / face.width
        my += y / face.height

        md += face.eye_distance / face.width

    average_middle_ratio_point = (mx / len(faces), my / len(faces))
    average_dist_ratio = md / len(faces)

    print("average middle point ratio ", average_middle_ratio_point)
    print("average eye distance ", average_dist_ratio * 100)

    c = 0
    for face in faces.values():
        c += 1
        path, file_name = os.path.split(face.path)
        abs_res_path = os.path.join(RES_DIR, file_name)

        ax, ay = face.middle_point
        bx, by = average_middle_ratio_point
        bx *= face.width
        by *= face.height
        dx = int(bx - ax)
        dy = int(by - ay)

        scale = (face.width * average_dist_ratio) / face.eye_distance

        if not face.path.endswith(".HEIC"):
            subprocess.call(
                f'magick "{face.path}" -auto-orient ' f'"{face.path}"',
                shell=True,
            )
        subprocess.call(
            f"convert {face.path} "
            f'-distort SRT "0,0 1 0 {dx},{dy}" '
            f'-distort SRT "{scale} 0" '
            f'-distort SRT "0" '
            f"-colorspace sRGB "
            f"{abs_res_path}",
            shell=True,
        )

        print(
            f"{c}/{len(faces.values())} saved {abs_res_path} with "
            f"{(dx, dy)} {scale}"
        )
        time.sleep(5)

    cv2.waitKey()


if __name__ == "__main__":
    main()
