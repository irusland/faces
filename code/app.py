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
from code.extractors.presenter import Presenter
from code.utils import with_performance_profile

from definitions import MODELS_DIR, PHOTOS_SRC_TEST_DIR

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
    presenter = Presenter()
    logger.info("Operators prepared")

    image_path_todo = os.path.join(PHOTOS_SRC_TEST_DIR, "IMG_4541.HEIC")
    image_path_reference = os.path.join(PHOTOS_SRC_TEST_DIR, "IMG_4557.HEIC")
    anchor_landmarks = None
    for image_path in (image_path_todo, image_path_reference):
        logger.info("processing %s", image_path)
        heic = file_manager.read_heif(image_path)
        pil_image = converter.pyheif_to_pil_image(heic)
        np_image = converter.pil_image_to_numpy_array(pil_image)
        for face_landmarks in predictor.get_landmarks(np_image):
            if anchor_landmarks is None:
                anchor_landmarks = face_landmarks
                print("reference set")

            operator_matrix = get_translation_operator_matrix(
                anchor_landmarks, face_landmarks
            )
            np_warped = warp_image(np_image, operator_matrix)
            # cv2.imshow("Frame", warped)
            # cv2.waitKey(0)
            # converter.numpy_array_to_pil_image(warped).show()
            painter.draw_points(pil_image, face_landmarks)
            # pil_image.show()
            file_manager.save_np_array_image(
                np_warped,
            )

        logger.info("processed %s", image_path)
        presenter.display(np_image)


if __name__ == "__main__":
    main()
