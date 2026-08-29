from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.media.entertainment import Entertainment
from app.models.interactions.rating import Rating
from app.models.interactions.entertainment_log import EntertainmentLog

from app.utils.media_serializer import build_media_response


def get_popular_media(
    db: Session,
    user_id: int,
    limit: int = 10
):
    # --------------------------------
    # Media already seen by the user
    # --------------------------------

    seen_ids = {
        entertainment_id
        for (entertainment_id,) in (
            db.query(EntertainmentLog.entertainment_id)
            .filter(
                EntertainmentLog.user_id == user_id
            )
            .all()
        )
    }

    # Also exclude anything the user has rated
    rated_ids = {
        entertainment_id
        for (entertainment_id,) in (
            db.query(Rating.entertainment_id)
            .filter(
                Rating.user_id == user_id
            )
            .all()
        )
    }

    seen_ids.update(rated_ids)

    # --------------------------------
    # Calculate popularity
    # --------------------------------

    popular = (
        db.query(
            Rating.entertainment_id,
            func.avg(Rating.rating).label("avg_rating"),
            func.count(Rating.id).label("rating_count")
        )
        .group_by(
            Rating.entertainment_id
        )
        .order_by(
            func.count(Rating.id).desc(),
            func.avg(Rating.rating).desc()
        )
        .all()
    )

    recommendations = []

    for row in popular:

        entertainment_id = row.entertainment_id

        if entertainment_id in seen_ids:
            continue

        media = (
            db.query(Entertainment)
            .filter(
                Entertainment.id == entertainment_id
            )
            .first()
        )

        if not media:
            continue

        recommendations.append({
            "media": build_media_response(media),
            "score": float(row.avg_rating)
        })

        if len(recommendations) >= limit:
            break

    return recommendations