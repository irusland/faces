import logging
import os
import sys
from code.extractors.converter import Converter
from code.extractors.landmarker import FacialPredictor
from code.extractors.painter import Painter
from code.extractors.presenter import Presenter
from code.extractors.reader import Reader
from code.utils import with_performance_profile

from definitions import MODELS_DIR, PHOTOS_SRC_TEST_DIR

FORMAT = "[%(filename)15s|%(funcName)15s:%(lineno)4s] %(message)s"
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__file__)


@with_performance_profile
def main():
    reader = Reader()
    converter = Converter()
    model_path = os.path.join(
        MODELS_DIR, "shape_predictor_68_face_landmarks.dat"
    )
    predictor = FacialPredictor(model_path)
    painter = Painter()
    presenter = Presenter()
    logger.info("Operators prepared")

    image_path = os.path.join(PHOTOS_SRC_TEST_DIR, "IMG_4541.HEIC")
    logger.info("processing %s", image_path)
    heic = reader.read_heif(image_path)
    pil_image = converter.pyheif_to_pil_image(heic)
    np_image = converter.pil_image_to_numpy_ndarray(pil_image)
    for face_landmarks in predictor.get_landmarks(np_image):
        painter.draw_points(pil_image, face_landmarks)
    logger.info("processed %s", image_path)

    pil_image.show()
    presenter.display(np_image)


if __name__ == "__main__":
    main()
