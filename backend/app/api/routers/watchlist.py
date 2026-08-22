from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.core.security import get_current_user
from app.models.user.user import User
from app.schemas.interactions.watchlist import (
    WatchlistCreate,
    WatchlistResponse
)
from app.services.watchlist_service import (
    add_to_watchlist,
    remove_from_watchlist,
    get_watchlist
)


router = APIRouter(
    prefix="/watchlist",
    tags=["Watchlist"]
)

@router.post(
    "/",
    response_model=WatchlistResponse
)
async def add_media_to_watchlist(
    request: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return add_to_watchlist(
        db=db,
        user=current_user,
        entertainment_id=request.entertainment_id
    )

@router.get(
    "/",
    response_model=list[WatchlistResponse]
)
async def get_user_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return get_watchlist(
        db=db,
        user=current_user
    )

@router.delete(
    "/{entertainment_id}"
)
async def remove_media_from_watchlist(
    entertainment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return remove_from_watchlist(
        db=db,
        user=current_user,
        entertainment_id=entertainment_id
    )