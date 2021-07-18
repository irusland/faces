from dependency_injector import containers, providers

from backend.db.redis import RedisDB, RedisSettings
from backend.extractors.converter import Converter
from backend.extractors.filemanager import FileManager
from backend.extractors.landmarker import FacialPredictor
from backend.extractors.painter import Painter


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    converter = providers.Singleton(Converter)

    file_manager = providers.Singleton(
        FileManager,
        converter=converter,
    )

    predictor = providers.Singleton(
        FacialPredictor,
        model_path=config.model_path,
    )

    painter = providers.Singleton(
        Painter,
    )

    db_settings = providers.Singleton(
        RedisSettings,
    )

    database = providers.Singleton(
        RedisDB,
        settings=db_settings,
    )

    source_dir: str
    result_dir: str
    image_reference_path: str
