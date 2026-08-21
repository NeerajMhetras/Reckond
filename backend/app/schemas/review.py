from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.entertainment import MediaResponse


class ReviewCreate(BaseModel):
    entertainment_id: int
    content: str = Field(
        min_length=1,
        max_length=5000
    )


class ReviewResponse(BaseModel):
    id: int
    entertainment_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    media: MediaResponse

class ReviewUpdate(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=5000
    )