from dependency_injector import containers, providers

from backend.db.redis import RedisDB, RedisSettings
from backend.extractors.converter import Converter
from backend.extractors.filemanager import FileManager
from backend.extractors.landmarker import FacialPredictor
from backend.extractors.painter import Painter
from backend.settings import (
    ProcessorSettings,
    ReferenceSettings,
    ResultSettings,
    SourceSettings,
)


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
        RedisDB,  # todo Interface
        settings=db_settings,
    )

    source_settings = providers.Singleton(
        SourceSettings,
    )
    result_settings = providers.Singleton(
        ResultSettings,
    )
    reference_settings = providers.Singleton(
        ReferenceSettings,
    )

    processor_settings = providers.Singleton(
        ProcessorSettings,
        source_settings=source_settings,
        result_settings=result_settings,
        reference_settings=reference_settings,
    )
