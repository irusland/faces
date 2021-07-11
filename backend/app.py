import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from cv2 import cv2
from dotenv import load_dotenv

from backend.db.database import Database, FacialData, MetaData
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
    scale,
    warp_image,
)
from backend.extractors.painter import Painter
from backend.file.utils import get_datetime_original, get_file_hash
from backend.utils import with_performance_profile
from definitions import (
    DEV_ENV_PATH,
    MODELS_DIR,
    PHOTOS_RES_TEST_DIR,
    PHOTOS_SRC_TEST_DIR,
)

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

    source_dir = PHOTOS_SRC_TEST_DIR
    result_dir = PHOTOS_RES_TEST_DIR
    # image_path_reference = path("IMG_4541.HEIC")
    image_path_reference = path("IMG_2149.HEIC")

    anchor_landmarks = None
    anchor_size = None
    is_processed, anchor_landmarks, anchor_size = process_image(
        image_path_reference,
        result_dir,
        file_manager,
        converter,
        database,
        predictor,
        painter,
        anchor_landmarks,
        anchor_size,
    )
    logger.debug("reference set")
    files = [image_path_reference]
    for (dirpath, dirnames, filenames) in os.walk(source_dir):
        files.extend(
            os.path.join(source_dir, filename) for filename in filenames
        )

    image_tasks = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        for image_path in files:
            future = executor.submit(
                process_image,
                *(
                    image_path,
                    result_dir,
                    file_manager,
                    converter,
                    database,
                    predictor,
                    painter,
                    anchor_landmarks,
                    anchor_size,
                ),
            )
            image_tasks[image_path] = future
    for image_path, task in image_tasks.items():
        is_processed, *_ = task.result()
        if not is_processed:
            logger.info("%s was not processed", image_path)
    logger.info("All done")


def process_image(
    image_path,
    result_dir,
    file_manager,
    converter,
    database,
    predictor,
    painter,
    anchor_landmarks,
    anchor_size,
):
    try:
        image_hash = get_file_hash(image_path)
        processed_image_path = os.path.join(result_dir, f"{image_hash}.jpg")

        logger.info(
            "processing %s (%s) -> %s",
            image_path,
            image_hash,
            processed_image_path,
        )
        pil_image = file_manager.read_pil_auto(image_path)
        np_image = converter.pil_image_to_numpy_array(pil_image)
        np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)

        landmarks = get_or_create_landmarks(
            image_hash, np_image, database, predictor
        )
        middle_point = converter.pil_image_center(pil_image)
        main_landmarks = predictor.select_main_face(landmarks, middle_point)
        np_warped = scale_adjust(
            main_landmarks, anchor_landmarks, anchor_size, pil_image, np_image
        )

        painter.draw_points(pil_image, main_landmarks)

        file_manager.save_np_array_image(np_warped, processed_image_path)

        datetime_original = get_datetime_original(image_path)
        meta = MetaData(
            image_hash=image_hash,
            origin_path=image_path,
            save_path=processed_image_path,
            size=pil_image.size,
            datetime_original=datetime_original,
        )
        database.save_info(meta)

        logger.info("processed %s", image_path)

        return True, main_landmarks, pil_image.size
    except Exception as e:
        logger.error("Failed %s", image_path, exc_info=e)
        return False, None, None


def get_or_create_landmarks(
    image_hash,
    np_image,
    database: Database,
    predictor: FacialPredictor,
):
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
    return landmarks


def scale_adjust(
    face_landmarks: np.ndarray,
    anchor_landmarks,
    anchor_size,
    pil_image,
    np_image,
) -> np.ndarray:
    if anchor_size is not None and pil_image.size != anchor_size:
        np_image = cv2.resize(np_image, anchor_size)
        face_landmarks = scale(face_landmarks, pil_image.size, anchor_size)
        logger.info("resize %s -> %s", pil_image.size, anchor_size)

    if anchor_landmarks is not None:
        operator_matrix = get_translation_operator_matrix(
            anchor_landmarks, face_landmarks
        )
        return warp_image(np_image, operator_matrix)
    return np_image


if __name__ == "__main__":
    load_dotenv(DEV_ENV_PATH)
    main()
