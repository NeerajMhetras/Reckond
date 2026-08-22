from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.media.entertainment import MediaResponse


class RatingCreate(BaseModel):
    entertainment_id: int

    rating: int = Field(
        ge=1,
        le=10
    )


class RatingResponse(BaseModel):
    id: int
    entertainment_id: int
    rating: int
    created_at: datetime
    updated_at: datetime
    media: MediaResponse