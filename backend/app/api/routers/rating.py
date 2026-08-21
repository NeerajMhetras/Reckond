from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.core.security import get_current_user

from app.models.user import User

from app.schemas.rating import (
    RatingCreate,
    RatingResponse
)

from app.services.rating_service import (
    create_or_update_rating,
    get_ratings,
    get_rating,
    delete_rating
)


router = APIRouter(
    prefix="/ratings",
    tags=["Ratings"]
)


@router.post(
    "/",
    response_model=RatingResponse
)
async def rate_media(
    request: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return create_or_update_rating(
        db=db,
        user=current_user,
        entertainment_id=request.entertainment_id,
        rating_value=request.rating
    )


@router.get(
    "/",
    response_model=list[RatingResponse]
)
async def get_user_ratings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return get_ratings(
        db=db,
        user=current_user
    )


@router.get(
    "/{entertainment_id}",
    response_model=RatingResponse
)
async def get_user_rating(
    entertainment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return get_rating(
        db=db,
        user=current_user,
        entertainment_id=entertainment_id
    )


@router.delete(
    "/{entertainment_id}"
)
async def remove_rating(
    entertainment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return delete_rating(
        db=db,
        user=current_user,
        entertainment_id=entertainment_id
    )