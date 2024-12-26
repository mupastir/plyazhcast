from datetime import datetime

from pydantic import BaseModel


class Episode(BaseModel):
    title: str
    number: int
    cover_url: str
    mp3_url: str
    themes: list[str]
    date_created: datetime
