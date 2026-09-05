from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.core.security import get_current_user

from app.models.user.user import User
from app.models.media.entertainment import Entertainment
from app.utils.media_serializer import build_media_response

from app.recommendation.recommender import recommend_for_user
from app.schemas.recommendation.recommendation import RecommendationResponse
from app.schemas.recommendation.recommendation import CollaborativeRecommendation

from app.recommendation.collaborative import (
    get_collaborative_recommendations
)

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get(
    "/for-you",
    response_model=list[RecommendationResponse]
)
async def get_for_you(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return recommend_for_user(
        db=db,
        user_id=current_user.id
    )
