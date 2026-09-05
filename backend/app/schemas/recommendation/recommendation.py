from pydantic import BaseModel

from app.schemas.media.entertainment import MediaResponse

class RecommendationResponse(BaseModel):
    media: MediaResponse
    score: float


class CollaborativeRecommendation(BaseModel):
    media: MediaResponse
    score: float