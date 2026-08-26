from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.media.entertainment import Entertainment
from app.models.interactions.entertainment_log import EntertainmentLog
from app.models.interactions.rating import Rating

from app.recommendation.content_based import get_similar_media

from app.utils.media_serializer import build_media_response


def recommend_for_user(
    db: Session,
    user_id: int,
    limit: int = 10
):
    # --------------------------------
    # Get user's ratings
    # --------------------------------

    ratings = (
        db.query(Rating)
        .filter(
            Rating.user_id == user_id
        )
        .all()
    )

    # --------------------------------
    # Get user's entertainment logs
    # --------------------------------

    logs = (
        db.query(EntertainmentLog)
        .filter(
            EntertainmentLog.user_id == user_id
        )
        .all()
    )

    # Nothing to learn from yet
    if not ratings:
        return []

    # --------------------------------
    # Items user has already seen
    # --------------------------------

    seen_ids = {
        log.entertainment_id
        for log in logs
    }

    # Also exclude anything they've rated
    seen_ids.update(
        rating.entertainment_id
        for rating in ratings
    )

    # --------------------------------
    # Find highly-rated items
    # --------------------------------

    liked_ratings = [
        rating
        for rating in ratings
        if rating.rating >= 6.5
    ]

    if not liked_ratings:
        return []

    # --------------------------------
    # Generate recommendation scores
    # --------------------------------

    recommendation_scores = defaultdict(float)

    for rating in liked_ratings:

        similar_items = get_similar_media(
            db=db,
            entertainment_id=rating.entertainment_id,
            limit=20
        )

        # Convert rating into a weight.
        #
        # 10 -> 1.0
        # 9  -> 0.9
        # 8  -> 0.8
        # 7  -> 0.7

        rating_weight = rating.rating / 10

        for result in similar_items:

            media = result["media"]
            similarity = result["score"]

            # Don't recommend something the
            # user already knows.
            if media.id in seen_ids:
                continue

            recommendation_scores[media.id] += (
                similarity * rating_weight
            )

    if not recommendation_scores:
        return []

    # --------------------------------
    # Rank recommendations
    # --------------------------------

    ranked = sorted(
        recommendation_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # --------------------------------
    # Fetch media objects
    # --------------------------------

    media_ids = [
        media_id
        for media_id, _ in ranked[:limit]
    ]

    media_list = (
        db.query(Entertainment)
        .filter(
            Entertainment.id.in_(media_ids)
        )
        .all()
    )

    media_map = {
        media.id: media
        for media in media_list
    }

    # --------------------------------
    # Build final response
    # --------------------------------

    return [
        {
            "media": build_media_response(
                media_map[media_id]
            ),
            "score": score
        }
        for media_id, score in ranked[:limit]
        if media_id in media_map
    ]