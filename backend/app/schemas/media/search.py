from pydantic import BaseModel

from app.models.media.entertainment import MediaType


class SearchResult(BaseModel):
    external_id: str
    title: str
    media_type: MediaType
    description: str | None = None
    release_date: str | None = None
    poster_url: str | None = None