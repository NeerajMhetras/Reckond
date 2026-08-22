from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.interactions.rating import Rating
from app.models.media.entertainment import Entertainment
from app.models.user.user import User

from app.utils.media_serializer import build_media_response


def create_or_update_rating(
    db: Session,
    user: User,
    entertainment_id: int,
    rating_value: int
):

    media = (
        db.query(Entertainment)
        .filter(
            Entertainment.id == entertainment_id
        )
        .first()
    )

    if not media:
        raise HTTPException(
            status_code=404,
            detail="Media not found"
        )

    existing = (
        db.query(Rating)
        .filter(
            Rating.user_id == user.id,
            Rating.entertainment_id == entertainment_id
        )
        .first()
    )

    if existing:

        existing.rating = rating_value

        db.commit()
        db.refresh(existing)

        rating = existing

    else:

        rating = Rating(
            user_id=user.id,
            entertainment_id=entertainment_id,
            rating=rating_value
        )

        db.add(rating)
        db.commit()
        db.refresh(rating)

    return {
        "id": rating.id,
        "entertainment_id": rating.entertainment_id,
        "rating": rating.rating,
        "created_at": rating.created_at,
        "updated_at": rating.updated_at,
        "media": build_media_response(
            rating.entertainment
        )
    }

def get_ratings(
    db: Session,
    user: User
):

    ratings = (
        db.query(Rating)
        .filter(
            Rating.user_id == user.id
        )
        .order_by(
            Rating.updated_at.desc()
        )
        .all()
    )

    return [
        {
            "id": rating.id,
            "entertainment_id": rating.entertainment_id,
            "rating": rating.rating,
            "created_at": rating.created_at,
            "updated_at": rating.updated_at,
            "media": build_media_response(
                rating.entertainment
            )
        }
        for rating in ratings
    ]

def get_rating(
    db: Session,
    user: User,
    entertainment_id: int
):

    rating = (
        db.query(Rating)
        .filter(
            Rating.user_id == user.id,
            Rating.entertainment_id == entertainment_id
        )
        .first()
    )

    if not rating:
        raise HTTPException(
            status_code=404,
            detail="Rating not found"
        )

    return {
        "id": rating.id,
        "entertainment_id": rating.entertainment_id,
        "rating": rating.rating,
        "created_at": rating.created_at,
        "updated_at": rating.updated_at,
        "media": build_media_response(
            rating.entertainment
        )
    }

def delete_rating(
    db: Session,
    user: User,
    entertainment_id: int
):

    rating = (
        db.query(Rating)
        .filter(
            Rating.user_id == user.id,
            Rating.entertainment_id == entertainment_id
        )
        .first()
    )

    if not rating:
        raise HTTPException(
            status_code=404,
            detail="Rating not found"
        )

    db.delete(rating)
    db.commit()

    return {
        "message": "Rating deleted successfully"
    }