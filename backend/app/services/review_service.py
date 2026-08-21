from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.entertainment import Entertainment
from app.models.user import User

from app.utils.media_serializer import build_media_response


def create_review(
    db: Session,
    user: User,
    entertainment_id: int,
    content: str
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
        db.query(Review)
        .filter(
            Review.user_id == user.id,
            Review.entertainment_id == entertainment_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Review already exists"
        )

    review = Review(
        user_id=user.id,
        entertainment_id=entertainment_id,
        content=content
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return {
        "id": review.id,
        "entertainment_id": review.entertainment_id,
        "content": review.content,
        "created_at": review.created_at,
        "updated_at": review.updated_at,
        "media": build_media_response(
            review.entertainment
        )
    }

def update_review(
    db: Session,
    user: User,
    entertainment_id: int,
    content: str
):

    review = (
        db.query(Review)
        .filter(
            Review.user_id == user.id,
            Review.entertainment_id == entertainment_id
        )
        .first()
    )

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    review.content = content

    db.commit()
    db.refresh(review)

    return {
        "id": review.id,
        "entertainment_id": review.entertainment_id,
        "content": review.content,
        "created_at": review.created_at,
        "updated_at": review.updated_at,
        "media": build_media_response(
            review.entertainment
        )
    }



def get_reviews(
    db: Session,
    user: User
):

    reviews = (
        db.query(Review)
        .filter(
            Review.user_id == user.id
        )
        .order_by(
            Review.updated_at.desc()
        )
        .all()
    )

    return [
        {
            "id": review.id,
            "entertainment_id": review.entertainment_id,
            "content": review.content,
            "created_at": review.created_at,
            "updated_at": review.updated_at,
            "media": build_media_response(
                review.entertainment
            )
        }
        for review in reviews
    ]


def get_review(
    db: Session,
    user: User,
    entertainment_id: int
):

    review = (
        db.query(Review)
        .filter(
            Review.user_id == user.id,
            Review.entertainment_id == entertainment_id
        )
        .first()
    )

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    return {
        "id": review.id,
        "entertainment_id": review.entertainment_id,
        "content": review.content,
        "created_at": review.created_at,
        "updated_at": review.updated_at,
        "media": build_media_response(
            review.entertainment
        )
    }


def delete_review(
    db: Session,
    user: User,
    entertainment_id: int
):

    review = (
        db.query(Review)
        .filter(
            Review.user_id == user.id,
            Review.entertainment_id == entertainment_id
        )
        .first()
    )

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    db.delete(review)
    db.commit()

    return {
        "message": "Review deleted successfully"
    }