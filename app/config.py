import os
from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class MongoDBSettings(BaseModel):
    db: str = "plyazhcast"
    username: str
    password: str
    host: str
    port: int = 27017
    alias: str = "default"


class Settings(BaseSettings):
    SECRET_KEY: str = "dev"
    TITLE: str = "Пляжкаст"
    IMAGE_UPLOAD_PATH: str = "/static/uploads/images"
    AUDIO_UPLOAD_PATH: str = "/static/uploads/audio"
    WTF_SCRF_SECRET_KEY: str
    HOST: str
    MONGODB_SETTINGS: MongoDBSettings


@lru_cache
def get_settings() -> Settings:
    return Settings(
        _env_file=os.environ.get("ENV_FILES", ".env").split(",")
    )  # type: ignore[call-arg]
