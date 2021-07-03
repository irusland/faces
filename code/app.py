import logging
import os
import sys
from code.extractors.converter import Converter
from code.extractors.filemanager import FileManager
from code.extractors.landmarker import FacialPredictor
from code.extractors.operator import (
    get_translation_operator_matrix,
    warp_image,
)
from code.extractors.painter import Painter
from code.file.utils import get_file_hash
from code.network.database import FacialData, TinyDatabase, TinyDBSettings
from code.utils import with_performance_profile

import numpy
from cv2 import cv2
from dotenv import load_dotenv

from definitions import (
    DEV_ENV_PATH,
    MODELS_DIR,
    PHOTOS_RES_TEST_DIR,
    PHOTOS_SRC_TEST_DIR,
    TINY_DB_FILE,
)

FORMAT = "[%(filename)15s|%(funcName)15s:%(lineno)4s] %(message)s"
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__file__)


@with_performance_profile
def main():
    file_manager = FileManager()
    converter = Converter()
    model_path = os.path.join(
        MODELS_DIR, "shape_predictor_68_face_landmarks.dat"
    )
    predictor = FacialPredictor(model_path)
    painter = Painter()
    db_settings = TinyDBSettings(storage_file=TINY_DB_FILE)
    database = TinyDatabase(db_settings)
    logger.info("Operators prepared")

    image_path_todo = os.path.join(PHOTOS_SRC_TEST_DIR, "IMG_4541.HEIC")
    image_path_reference = os.path.join(PHOTOS_SRC_TEST_DIR, "IMG_4557.HEIC")
    anchor_landmarks = None
    for image_path in (image_path_todo, image_path_reference):
        image_hash = get_file_hash(image_path)
        processed_image_path = os.path.join(
            PHOTOS_RES_TEST_DIR, f"{image_hash}.jpg"
        )

        logger.info("processing %s (%s)", image_path, image_hash)
        heic = file_manager.read_heif(image_path)
        pil_image = converter.pyheif_to_pil_image(heic)
        np_image = converter.pil_image_to_numpy_array(pil_image)
        np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)

        if face_data := database.get_landmarks(image_hash):
            landmarks = [numpy.array(face) for face in face_data.landmarks]
        else:
            landmarks = predictor.get_landmarks(np_image)
            tuple_marks = [
                list(map(tuple, face_landmarks))
                for face_landmarks in landmarks
            ]
            data = FacialData(image_hash=image_hash, landmarks=tuple_marks)
            database.save_landmarks(data)

        for i, face_landmarks in enumerate(landmarks):
            logger.info("")
            if anchor_landmarks is None:
                anchor_landmarks = face_landmarks
                print("reference set")

            operator_matrix = get_translation_operator_matrix(
                anchor_landmarks, face_landmarks
            )
            np_warped = warp_image(np_image, operator_matrix)
            painter.draw_points(pil_image, face_landmarks)
            file_manager.save_np_array_image(np_warped, processed_image_path)

        logger.info("processed %s", image_path)


if __name__ == "__main__":
    load_dotenv(DEV_ENV_PATH)
    main()
