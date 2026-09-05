from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.media.entertainment import Entertainment
from app.models.interactions.entertainment_log import EntertainmentLog
from app.models.interactions.rating import Rating

from app.recommendation.content_based import get_similar_media
from app.recommendation.popularity import get_popular_media

from app.recommendation.collaborative import get_collaborative_recommendations

from app.utils.media_serializer import build_media_response


def get_rating_weight(rating: int) -> float:
    """
    Convert a 1-10 rating into a preference weight.

    10 -> +1.0
     9 -> +0.8
     8 -> +0.6
     7 -> +0.4
     6 -> +0.2
     5 ->  0.0
     4 -> -0.2
     3 -> -0.4
     2 -> -0.6
     1 -> -0.8
    """

    return (rating - 5) / 5

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
    # No ratings → popularity fallback
    # --------------------------------

    if not ratings:
        return get_popular_media(
            db=db,
            user_id=user_id,
            limit=limit
        )

    # ================================================
    # CONTENT-BASED SCORES
    # ================================================

    content_scores = defaultdict(float)

    for rating in ratings:

        rating_weight = get_rating_weight(
            rating.rating
        )

        # Rating of 5 has no influence
        if rating_weight == 0:
            continue

        similar_items = get_similar_media(
            db=db,
            entertainment_id=rating.entertainment_id,
            limit=20
        )

        for result in similar_items:

            media = result["media"]
            similarity = result["score"]

            if media.id in seen_ids:
                continue

            content_scores[media.id] += (
                similarity * rating_weight
            )

    # ================================================
    # COLLABORATIVE SCORES
    # ================================================

    collaborative_results = (
        get_collaborative_recommendations(
            db=db,
            user_id=user_id,
            limit=50
        )
    )

    collaborative_scores = {
        media_id: score
        for media_id, score in collaborative_results
        if media_id not in seen_ids
    }

    # ================================================
    # NORMALIZE CONTENT SCORES
    # ================================================

    if content_scores:

        max_content = max(
            content_scores.values()
        )

        min_content = min(
            content_scores.values()
        )

        if max_content != min_content:

            content_scores = {
                media_id:
                (score - min_content)
                / (max_content - min_content)

                for media_id, score
                in content_scores.items()
            }

        else:

            content_scores = {
                media_id: 1.0
                for media_id in content_scores
            }

    # ================================================
    # NORMALIZE COLLABORATIVE SCORES
    # ================================================

    if collaborative_scores:

        max_collaborative = max(
            collaborative_scores.values()
        )

        min_collaborative = min(
            collaborative_scores.values()
        )

        if max_collaborative != min_collaborative:

            collaborative_scores = {
                media_id:
                (score - min_collaborative)
                / (max_collaborative - min_collaborative)

                for media_id, score
                in collaborative_scores.items()
            }

        else:

            collaborative_scores = {
                media_id: 1.0
                for media_id in collaborative_scores
            }

    # ================================================
    # COMBINE CANDIDATES
    # ================================================

    candidate_ids = (
        set(content_scores.keys())
        |
        set(collaborative_scores.keys())
    )

    if not candidate_ids:
        return get_popular_media(
            db=db,
            user_id=user_id,
            limit=limit
        )

    # ================================================
    # HYBRID SCORE
    # ================================================

    recommendation_scores = {}

    for media_id in candidate_ids:

        content_score = content_scores.get(
            media_id,
            0.0
        )

        collaborative_score = collaborative_scores.get(
            media_id,
            0.0
        )

        hybrid_score = (
            0.7 * content_score
            +
            0.3 * collaborative_score
        )

        recommendation_scores[media_id] = (
            hybrid_score
        )

    # ================================================
    # RANK
    # ================================================

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