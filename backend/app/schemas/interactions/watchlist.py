from datetime import datetime

from pydantic import BaseModel

from app.schemas.media.entertainment import MediaResponse


class WatchlistCreate(BaseModel):
    entertainment_id: int


class WatchlistResponse(BaseModel):
    id: int
    entertainment_id: int
    created_at: datetime
    media: MediaResponse