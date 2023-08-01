import os
from abc import ABC
from enum import Enum

from flask import current_app


class FileTypes(str, Enum):
    AUDIO = "AUDIO"
    IMAGE = "IMAGE"


class BaseFileUploader(ABC):
    def __init__(self, file_type: FileTypes, name: str, data):
        self._file_type = file_type
        self._name = name
        self._data = data

    def upload(self) -> str:
        pass


class LocalFileUploader(BaseFileUploader):
    def upload(self):
        relative_path = os.path.join(
            current_app.config[f"{self._file_type}_UPLOAD_PATH"], self._name
        )
        upload_path = f'{current_app.config["BASE_PATH"]}{relative_path}'
        self._data.save(upload_path)
        return f"{current_app.config['HOST']}{relative_path}"
