from collections import defaultdict
from math import sqrt

from sqlalchemy.orm import Session

from app.models.interactions.rating import Rating


def build_rating_matrix(db: Session):
    ratings = (
        db.query(Rating)
        .all()
    )

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
    vector_b: dict
):
    common_users = (
        set(vector_a.keys())
        &
        set(vector_b.keys())
    )

    if not common_users:
        return 0.0

    dot_product = 0.0
    magnitude_a = 0.0
    magnitude_b = 0.0

    for user_id in common_users:

        rating_a = vector_a[user_id]
        rating_b = vector_b[user_id]

        dot_product += rating_a * rating_b

        magnitude_a += rating_a ** 2
        magnitude_b += rating_b ** 2

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (sqrt(magnitude_a) * sqrt(magnitude_b))


def get_collaborative_similar_items(
    db: Session,
    entertainment_id: int,
    limit: int = 20
):
    matrix = build_rating_matrix(db)

    item_vectors = build_item_vectors(matrix)

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
            vector
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