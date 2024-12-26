import httpx
from typing import Optional, List, Type, TypeVar, Literal
from pydantic import BaseModel
from copy import deepcopy

from app.models.openai.response import Answer

OAI_V1 = "https://api.openai.com/v1/"

T = TypeVar("T", bound=BaseModel)


class OpenAIError(Exception):
    pass


class OpenAI:
    def __init__(
        self,
        api_key: str,
        organization: Optional[str] = None,
        model: str = "dall-e-3",
    ):
        self._model = model
        self._auth_header = deepcopy(
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )
        if organization:
            self._auth_header["OpenAI-Organization"] = organization
        self._api_key = api_key

    async def call(self, endpoint: str, return_type: Type[T], payload: dict = {}) -> T:
        url = OAI_V1 + endpoint
        headers = self._auth_header
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                raise OpenAIError(f"Error: {response.status_code} - {response.text}")
            js = response.json()
            return return_type.model_validate(js)

    async def image_generate(
        self,
        prompt: str,
        n: int = 1,
        size: str = "1024x1024",
        quality: str = "hd",
        style: Literal["vivid", "natural"] = "vivid",
    ) -> Answer:
        model: str = self._model
        req = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
            "quality": quality,
            "style": style,
        }
        response = await self.call("images/generations", Answer, req)
        return response
