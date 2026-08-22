from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.interactions.watchlist import Watchlist
from app.models.media.entertainment import Entertainment
from app.models.user.user import User

from app.utils.media_serializer import build_media_response

def add_to_watchlist(
    db: Session,
    user: User,
    entertainment_id: int
):

    media = (
        db.query(Entertainment)
        .filter(Entertainment.id == entertainment_id)
        .first()
    )

    if not media:
        raise HTTPException(
            status_code=404,
            detail="Media not found"
        )

    existing = (
        db.query(Watchlist)
        .filter(
            Watchlist.user_id == user.id,
            Watchlist.entertainment_id == entertainment_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Media already in watchlist"
        )

    item = Watchlist(
        user_id=user.id,
        entertainment_id=entertainment_id
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "entertainment_id": item.entertainment_id,
        "created_at": item.created_at,
        "media": build_media_response(item.entertainment)
    }

def remove_from_watchlist(
    db: Session,
    user: User,
    entertainment_id: int
):

    item = (
        db.query(Watchlist)
        .filter(
            Watchlist.user_id == user.id,
            Watchlist.entertainment_id == entertainment_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Media is not in watchlist"
        )

    db.delete(item)
    db.commit()

    return {
        "message": "Media removed from watchlist"
    }

def get_watchlist(
    db: Session,
    user: User
):

    items = (
        db.query(Watchlist)
        .filter(
            Watchlist.user_id == user.id
        )
        .order_by(
            Watchlist.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": item.id,
            "entertainment_id": item.entertainment_id,
            "created_at": item.created_at,
            "media": build_media_response(
                item.entertainment
            )
        }
        for item in items
    ]