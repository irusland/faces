import logging
import os
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import List, Tuple

import numpy as np
import tqdm
from cv2 import cv2
from dependency_injector.wiring import Provide, inject

from backend.container import Container
from backend.db.database import CacheDatabase, Database, FacialData, MetaData
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
from backend.file.utils import (
    get_datetime_original,
    get_file_hash,
    get_paths_to_process,
)
from backend.utils import with_performance_profile

logger = logging.getLogger(__file__)


@inject
@with_performance_profile
def process_images(
    source_dir: str = Provide[Container.config.source_dir],
    result_dir: str = Provide[Container.config.result_dir],
    image_reference_path: str = Provide[Container.config.image_reference_path],
    file_manager: FileManager = Provide[Container.file_manager],
    converter: Converter = Provide[Container.converter],
    database: CacheDatabase = Provide[Container.database],
    predictor: FacialPredictor = Provide[Container.predictor],
    painter: Painter = Provide[Container.painter],
):
    logger.info("IN\t%s", source_dir)
    logger.info("OUT\t%s", result_dir)
    logger.info("REF\t%s", image_reference_path)

    anchor_landmarks = None
    anchor_size = None
    is_processed, anchor_landmarks, anchor_size, _ = process_image(
        image_path=image_reference_path,
        result_dir=result_dir,
        file_manager=file_manager,
        converter=converter,
        database=database,
        predictor=predictor,
        painter=painter,
        anchor_landmarks=anchor_landmarks,
        anchor_size=anchor_size,
        override=True,
    )
    logger.debug("reference set")

    files = get_paths_to_process(source_dir)

    process_image_path = partial(
        process_image,
        result_dir=result_dir,
        file_manager=file_manager,
        converter=converter,
        database=database,
        predictor=predictor,
        painter=painter,
        anchor_landmarks=anchor_landmarks,
        anchor_size=anchor_size,
    )
    failed = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        tasks = [executor.submit(process_image_path, file) for file in files]

        for future in tqdm.tqdm(futures.as_completed(tasks), total=len(files)):
            is_processed, _, _, image_path = future.result()
            if not is_processed:
                failed.append(image_path)

    for path_ in failed:
        logger.info("%s was not processed", path_)


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
    override: bool = False,
):
    try:
        image_hash = get_file_hash(image_path)
        processed_image_path = os.path.join(result_dir, f"{image_hash}.jpg")

        logger.debug(
            "processing %s (%s) -> %s",
            image_path,
            image_hash,
            processed_image_path,
        )
        pil_image = file_manager.read_pil_auto(image_path)
        np_image = converter.pil_image_to_numpy_array(pil_image)
        np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)

        landmarks, was_created = _get_or_create_landmarks(
            image_hash, np_image, database, predictor
        )
        exists = os.path.isfile(processed_image_path)
        if was_created or override or not exists:
            middle_point = converter.pil_image_center(pil_image)
            main_landmarks = predictor.select_main_face(
                landmarks, middle_point
            )
            np_warped = _scale_adjust(
                main_landmarks,
                anchor_landmarks,
                anchor_size,
                pil_image,
                np_image,
            )
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

            logger.debug("Processed %s", image_path)
            return True, main_landmarks, pil_image.size, image_path

        logger.debug("Already processed %s", image_path)
        return True, None, None, image_path
    except Exception as e:
        logger.error("Failed %s", image_path, exc_info=e)
        return False, None, None, image_path


def _save_landmarks(
    image_hash: str, landmarks: np.ndarray, database: Database
) -> None:
    data = FacialData(
        image_hash=image_hash,
        landmarks=np_landmarks_to_str(landmarks),
    )
    database.save_landmarks(data)


def _get_or_create_landmarks(
    image_hash: str,
    np_image: np.ndarray,
    database: Database,
    predictor: FacialPredictor,
) -> Tuple[List[np.ndarray], bool]:
    face_data = database.get_landmarks(image_hash)
    if face_data:
        landmarks = str_landmarks_to_np(face_data.landmarks)
        if len(landmarks) > 0:
            logger.debug("Recovered facial data %s", face_data)
            return landmarks, False

    logger.debug("Recognizing facial data %s", face_data)
    landmarks = predictor.get_landmarks(np_image)
    _save_landmarks(image_hash, landmarks, database)
    return landmarks, True


def _scale_adjust(
    face_landmarks: np.ndarray,
    anchor_landmarks,
    anchor_size,
    pil_image,
    np_image,
) -> np.ndarray:
    if anchor_size is not None and pil_image.size != anchor_size:
        np_image = cv2.resize(np_image, anchor_size)
        face_landmarks = scale(face_landmarks, pil_image.size, anchor_size)
        logger.debug("resize %s -> %s", pil_image.size, anchor_size)

    if anchor_landmarks is not None:
        operator_matrix = get_translation_operator_matrix(
            anchor_landmarks, face_landmarks
        )
        return warp_image(np_image, operator_matrix)
    return np_image
