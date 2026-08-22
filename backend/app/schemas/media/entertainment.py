from pydantic import BaseModel,ConfigDict
from app.models.media.entertainment import MediaType
from datetime import date
from typing import Any

class MediaImportRequest(BaseModel):
    external_id: str
    media_type: MediaType 


class MediaResponse(BaseModel):
    id: int
    title: str
    description: str | None
    poster_url: str | None
    release_date: date | None
    media_type: MediaType
    language: str | None
    external_id: str | None
    external_source: str | None

    details: Any = None

    model_config = ConfigDict(
        from_attributes=True
    )

class MediaListResponse(BaseModel):
    items: list[MediaResponse]
    total: int
    skip: int
    limit: int