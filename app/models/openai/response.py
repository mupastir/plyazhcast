from pydantic import BaseModel, HttpUrl

class UrlData(BaseModel):
    url: HttpUrl


class Answer(BaseModel):
    data: list[UrlData]
