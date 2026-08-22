from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.core.security import get_current_user

from app.models.user.user import User

from app.schemas.interactions.review import (
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate
)

from app.services.review_service import (
    create_review,
    update_review,
    get_reviews,
    get_review,
    delete_review
)


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)

@router.post(
    "/",
    response_model=ReviewResponse
)
async def add_review(
    request: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return create_review(
        db=db,
        user=current_user,
        entertainment_id=request.entertainment_id,
        content=request.content
    )

@router.get(
    "/",
    response_model=list[ReviewResponse]
)
async def get_user_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return get_reviews(
        db=db,
        user=current_user
    )


@router.get(
    "/{entertainment_id}",
    response_model=ReviewResponse
)
async def get_user_review(
    entertainment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return get_review(
        db=db,
        user=current_user,
        entertainment_id=entertainment_id
    )


@router.put(
    "/{entertainment_id}",
    response_model=ReviewResponse
)
async def edit_review(
    entertainment_id: int,
    request: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return update_review(
        db=db,
        user=current_user,
        entertainment_id=entertainment_id,
        content=request.content
    )

@router.put(
    "/{entertainment_id}",
    response_model=ReviewResponse
)
async def edit_review(
    entertainment_id: int,
    request: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return update_review(
        db=db,
        user=current_user,
        entertainment_id=entertainment_id,
        content=request.content
    )

@router.delete(
    "/{entertainment_id}"
)
async def remove_review(
    entertainment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return delete_review(
        db=db,
        user=current_user,
        entertainment_id=entertainment_id
    )