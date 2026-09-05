from collections import defaultdict
from math import sqrt

from sqlalchemy.orm import Session

from app.models.interactions.rating import Rating


def build_rating_matrix(db: Session, user_ids=None, entertainment_ids=None):
    query = db.query(Rating)

    if user_ids is not None:
        query = query.filter(Rating.user_id.in_(user_ids))

    if entertainment_ids is not None:
        query = query.filter(Rating.entertainment_id.in_(entertainment_ids))

    ratings = query.all()

    matrix = defaultdict(dict)

    for rating in ratings:
        matrix[rating.user_id][rating.entertainment_id] = rating.rating

    return matrix


def build_item_vectors(matrix):
    item_vectors = defaultdict(dict)

    for user_id, user_ratings in matrix.items():

        for entertainment_id, rating in user_ratings.items():

            item_vectors[entertainment_id][user_id] = rating

    return item_vectors


def cosine_similarity(
    vector_a: dict,
    vector_b: dict,
    user_averages: dict,
    min_common_users: int = 3
):

    common_users = (
        set(vector_a.keys())
        &
        set(vector_b.keys())
    )

    if len(common_users) < min_common_users:
        return 0.0

    dot_product = 0.0
    magnitude_a = 0.0
    magnitude_b = 0.0

    for user_id in common_users:

        rating_a = (
            vector_a[user_id]
            - user_averages[user_id]
        )

        rating_b = (
            vector_b[user_id]
            - user_averages[user_id]
        )

        dot_product += rating_a * rating_b

        magnitude_a += rating_a ** 2
        magnitude_b += rating_b ** 2

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return (
        dot_product
        /
        (
            sqrt(magnitude_a)
            *
            sqrt(magnitude_b)
        )
    )


def get_collaborative_similar_items(
    db: Session,
    entertainment_id: int,
    limit: int = 20
):

    matrix = build_rating_matrix(db)

    item_vectors = build_item_vectors(matrix)

    user_averages = build_user_averages(matrix)

    target_vector = item_vectors.get(
        entertainment_id
    )

    if not target_vector:
        return []

    similarities = []

    for item_id, vector in item_vectors.items():

        if item_id == entertainment_id:
            continue

        score = cosine_similarity(
            target_vector,
            vector,
            user_averages
        )

        if score <= 0:
            continue

        similarities.append(
            (item_id, score)
        )

    similarities.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return similarities[:limit]

def get_collaborative_recommendations(
    db: Session,
    user_id: int,
    limit: int = 20
):
    user_ratings = (
        db.query(Rating)
        .filter(Rating.user_id == user_id)
        .all()
    )

    if not user_ratings:
        return []

    rated_items = {rating.entertainment_id for rating in user_ratings}

    # Only users who rated one of this user's items can contribute to
    # cosine similarity with that user's item vectors.
    relevant_user_ids = {
        rating_user_id
        for (rating_user_id,) in db.query(Rating.user_id)
        .filter(Rating.entertainment_id.in_(rated_items))
        .distinct()
        .all()
    }

    matrix = build_rating_matrix(db, user_ids=relevant_user_ids)
    item_vectors = build_item_vectors(matrix)
    user_averages = build_user_averages(matrix)

    user_ratings = matrix.get(user_id)

    if not user_ratings:
        return []

    recommendations = defaultdict(float)

    rated_items = set(user_ratings.keys())

    for item_id, user_rating in user_ratings.items():

        # We don't want low-rated items to influence
        # recommendations too much.
        if user_rating < 7:
            continue

        target_vector = item_vectors.get(item_id)

        if not target_vector:
            continue

        for other_item_id, other_vector in item_vectors.items():

            # User already rated this item.
            if other_item_id in rated_items:
                continue

            similarity = cosine_similarity(
                target_vector,
                other_vector,
                user_averages
            )

            if similarity <= 0:
                continue

            recommendations[other_item_id] += (
                similarity * user_rating
            )

    ranked = sorted(
        recommendations.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:limit]

def build_user_averages(matrix):

    averages = {}

    for user_id, ratings in matrix.items():

        if not ratings:
            continue

        averages[user_id] = (
            sum(ratings.values())
            / len(ratings)
        )

    return averages