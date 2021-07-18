import os

from pydantic import BaseSettings, validator


class PathSettings(BaseSettings):
    path: str

    @validator("path", pre=True)
    def path_absolute(cls, v):
        return os.path.abspath(v)


class SourceSettings(PathSettings):
    class Config:
        env_prefix = "SOURCE_"


class ResultSettings(PathSettings):
    class Config:
        env_prefix = "RESULT_"


class ReferenceSettings(PathSettings):
    class Config:
        env_prefix = "REFERENCE_"


class ProcessorSettings(BaseSettings):
    source_settings: SourceSettings
    result_settings: ResultSettings
    reference_settings: ReferenceSettings
