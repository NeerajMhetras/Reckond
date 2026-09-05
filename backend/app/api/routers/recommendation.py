import logging

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
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
from app.core.cache import cache, recommendation_cache_key
from app.core.config import settings


logger = logging.getLogger(__name__)

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
    cache_key = recommendation_cache_key(current_user.id)
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info("Recommendation cache HIT user_id=%s", current_user.id)
        return cached

    logger.info("Recommendation cache MISS user_id=%s", current_user.id)
    recommendations = recommend_for_user(
        db=db,
        user_id=current_user.id
    )
    cache.set(
        cache_key,
        jsonable_encoder(recommendations),
        settings.RECOMMENDATION_CACHE_TTL,
    )
    return recommendations
