from pydantic import BaseModel


class GameDetailsResponse(BaseModel):
    platforms: list[str] = []