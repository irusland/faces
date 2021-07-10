import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from cv2 import cv2
from dotenv import load_dotenv

from backend.db.database import Database, FacialData
from backend.db.redis import RedisDB, RedisSettings
from backend.extractors.converter import Converter
from backend.extractors.filemanager import FileManager
from backend.extractors.landmarker import (
    FacialPredictor,
    np_landmarks_to_str,
    str_landmarks_to_np,
)
from backend.extractors.operator import (
    get_translation_operator_matrix,
    warp_image, scale,
)
from backend.extractors.painter import Painter
from backend.file.utils import get_file_hash
from backend.utils import with_performance_profile
from definitions import (
    DEV_ENV_PATH,
    MODELS_DIR,
    PHOTOS_RES_TEST_DIR,
    PHOTOS_SRC_TEST_DIR,
    TINY_DB_FILE,
)
from PIL import Image

FORMAT = (
    "[%(thread)15d |%(filename)15s|%(funcName)15s:%(lineno)4s] %(message)s"
)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__file__)


def path(filename: str) -> str:
    return os.path.join(PHOTOS_SRC_TEST_DIR, filename)


@with_performance_profile
def main():
    converter = Converter()
    file_manager = FileManager(converter)
    model_path = os.path.join(
        MODELS_DIR, "shape_predictor_68_face_landmarks.dat"
    )
    predictor = FacialPredictor(model_path)
    painter = Painter()
    db_settings = RedisSettings()
    database = RedisDB(db_settings)
    logger.info("Operators prepared")

    image_path_todo = os.path.join(PHOTOS_SRC_TEST_DIR, "IMG_4541.HEIC")
    image_path_reference = os.path.join(PHOTOS_SRC_TEST_DIR, "IMG_4557.HEIC")

    anchor_landmarks = None
    anchor_size = None
    anchor_landmarks, anchor_size = process_image(
        image_path_reference,
        file_manager,
        converter,
        database,
        predictor,
        painter,
        anchor_landmarks,
        anchor_size,
    )

    image_tasks = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for image_path in (
            image_path_reference,
            image_path_todo,
            path("IMG_5069.HEIC"),
            path("IMG_0588.HEIC"),
            path("IMG_0005.HEIC"),
            path("IMG_0009.HEIC"),
            path("IMG_0518.HEIC"),
            path("IMG_0578.HEIC"),
            path("IMG_8800.jpg"),
            path("IMG_8808.JPG"),
        ):
            future = executor.submit(
                process_image,
                *(
                    image_path,
                    file_manager,
                    converter,
                    database,
                    predictor,
                    painter,
                    anchor_landmarks,
                    anchor_size,
                ),
            )
            image_tasks.append(future)
    for task in image_tasks:
        task.result()
    logger.info('All done')


def process_image(
    image_path,
    file_manager: FileManager,
    converter: Converter,
    database: Database,
    predictor: FacialPredictor,
    painter: Painter,
    anchor_landmarks,
    anchor_size,
):
    image_hash = get_file_hash(image_path)
    processed_image_path = os.path.join(
        PHOTOS_RES_TEST_DIR, f"{image_hash}.jpg"
    )

    logger.info("processing %s (%s)", image_path, image_hash)
    pil_image = file_manager.read_pil_auto(image_path)
    np_image = converter.pil_image_to_numpy_array(pil_image)
    np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)

    face_data = database.get_landmarks(image_hash)
    if face_data:
        landmarks = str_landmarks_to_np(face_data.landmarks)
    else:
        landmarks = list(predictor.get_landmarks(np_image))
        data = FacialData(
            image_hash=image_hash,
            landmarks=np_landmarks_to_str(landmarks),
        )
        database.save_landmarks(data)

    for face_landmarks in landmarks:
        if anchor_landmarks is None:
            anchor_size = pil_image.size
            anchor_landmarks = face_landmarks
            logger.debug("reference set")

        if anchor_size and pil_image.size != anchor_size:
            np_image = cv2.resize(np_image, anchor_size)
            face_landmarks = scale(face_landmarks, pil_image.size, anchor_size)
            logger.info("resize %s -> %s", pil_image.size, anchor_size)

        operator_matrix = get_translation_operator_matrix(
            anchor_landmarks, face_landmarks
        )

        np_warped = warp_image(np_image, operator_matrix)
        pil_image = pil_image.resize(anchor_size, Image.ANTIALIAS)
        painter.draw_points(pil_image, face_landmarks)
        pil_image.show()
        file_manager.save_np_array_image(np_warped, processed_image_path)

    logger.info("processed %s", image_path)
    return anchor_landmarks, anchor_size

if __name__ == "__main__":
    load_dotenv(DEV_ENV_PATH)
    main()
