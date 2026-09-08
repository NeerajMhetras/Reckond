from collections import defaultdict
from math import sqrt

from sqlalchemy.orm import Session

from app.models.interactions.rating import Rating


MIN_COMMON_USERS = 3
MIN_RATING_FOR_RECOMMENDATION = 7


def build_rating_matrix(
    db: Session,
    user_ids=None,
    entertainment_ids=None,
):
    query = db.query(Rating)

    if user_ids is not None:
        query = query.filter(
            Rating.user_id.in_(user_ids)
        )

    if entertainment_ids is not None:
        query = query.filter(
            Rating.entertainment_id.in_(entertainment_ids)
        )

    ratings = query.all()

    matrix = defaultdict(dict)

    for rating in ratings:
        matrix[rating.user_id][rating.entertainment_id] = rating.rating

    return matrix


def build_item_vectors(matrix):
    """
    Convert:

        user -> {item: rating}

    into:

        item -> {user: rating}
    """

    item_vectors = defaultdict(dict)

    for user_id, user_ratings in matrix.items():
        for entertainment_id, rating in user_ratings.items():
            item_vectors[entertainment_id][user_id] = rating

    return item_vectors


def build_user_averages(matrix):
    averages = {}

    for user_id, ratings in matrix.items():

        if not ratings:
            continue

        averages[user_id] = (
            sum(ratings.values()) / len(ratings)
        )

    return averages


def build_centered_vectors(
    item_vectors,
    user_averages,
):
    """
    Convert raw ratings into user-mean-centered ratings.

    item -> {
        user: rating - user's average
    }
    """

    centered_vectors = {}

    for item_id, vector in item_vectors.items():

        centered = {}

        for user_id, rating in vector.items():

            centered[user_id] = (
                rating - user_averages[user_id]
            )

        centered_vectors[item_id] = centered

    return centered_vectors


def build_vector_norms(centered_vectors):
    """
    Precompute ||vector|| for every item.
    """

    norms = {}

    for item_id, vector in centered_vectors.items():

        magnitude = sum(
            value * value
            for value in vector.values()
        )

        norms[item_id] = sqrt(magnitude)

    return norms


def build_user_item_index(matrix):
    """
    Build:

        user -> items

    This is used to find candidate items that share
    users with a target item.
    """

    user_items = {}

    for user_id, ratings in matrix.items():
        user_items[user_id] = set(ratings.keys())

    return user_items


def build_candidate_common_users(
    target_item_id,
    target_users,
    user_item_index,
    rated_items,
    min_common_users=MIN_COMMON_USERS,
):
    """
    Find candidate items that have enough users in common
    with the target item.

    Returns:

        {
            candidate_item_id: number_of_common_users
        }
    """

    common_user_counts = defaultdict(int)

    for user_id in target_users:

        items = user_item_index.get(
            user_id,
            ()
        )

        for item_id in items:

            # The user already rated this item.
            if item_id in rated_items:
                continue

            common_user_counts[item_id] += 1

    return {
        item_id: count
        for item_id, count in common_user_counts.items()
        if count >= min_common_users
    }


def cosine_similarity(
    vector_a,
    vector_b,
    norm_a,
    norm_b,
    min_common_users=MIN_COMMON_USERS,
):
    """
    Calculate cosine similarity between two
    already-centered item vectors.

    The vectors have already had each user's
    average rating subtracted.
    """

    # Iterate over the smaller vector.
    if len(vector_a) > len(vector_b):
        vector_a, vector_b = vector_b, vector_a

    common_users = 0
    dot_product = 0.0

    for user_id, rating_a in vector_a.items():

        rating_b = vector_b.get(user_id)

        if rating_b is None:
            continue

        common_users += 1

        if common_users >= min_common_users:
            dot_product += (
                rating_a * rating_b
            )

        else:
            dot_product += (
                rating_a * rating_b
            )

    if common_users < min_common_users:
        return 0.0

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return (
        dot_product
        / (norm_a * norm_b)
    )


def get_collaborative_recommendations(
    db: Session,
    user_id: int,
    limit: int = 20,
):
    """
    Item-based collaborative filtering.

    Algorithm:

    1. Get current user's ratings.
    2. Find users who rated at least one of those items.
    3. Build rating matrix for those users.
    4. Build item vectors.
    5. Center ratings around each user's average.
    6. Generate candidate items using shared users.
    7. Only calculate cosine similarity for candidates
       with >= MIN_COMMON_USERS shared users.
    8. Weight similarity by the current user's rating.
    9. Rank candidates.
    """

    # ==================================================
    # 1. Get current user's ratings
    # ==================================================

    user_ratings = (
        db.query(Rating)
        .filter(
            Rating.user_id == user_id
        )
        .all()
    )

    if not user_ratings:
        return []

    rated_items = {
        rating.entertainment_id
        for rating in user_ratings
    }

    # ==================================================
    # 2. Find relevant users
    # ==================================================

    relevant_user_ids = {
        rating_user_id
        for (rating_user_id,) in (
            db.query(Rating.user_id)
            .filter(
                Rating.entertainment_id.in_(
                    rated_items
                )
            )
            .distinct()
            .all()
        )
    }

    if not relevant_user_ids:
        return []

    # ==================================================
    # 3. Build rating matrix
    # ==================================================

    matrix = build_rating_matrix(
        db,
        user_ids=relevant_user_ids,
    )

    # ==================================================
    # 4. Build item vectors
    # ==================================================

    item_vectors = build_item_vectors(
        matrix
    )

    # ==================================================
    # 5. Build user averages
    # ==================================================

    user_averages = build_user_averages(
        matrix
    )

    # ==================================================
    # 6. Center item vectors
    # ==================================================

    centered_vectors = build_centered_vectors(
        item_vectors,
        user_averages,
    )

    # ==================================================
    # 7. Precompute vector norms
    # ==================================================

    vector_norms = build_vector_norms(
        centered_vectors
    )

    # ==================================================
    # 8. Build user -> items index
    # ==================================================

    user_item_index = build_user_item_index(
        matrix
    )

    # Use the matrix version of the current user's
    # ratings because it is guaranteed to belong to
    # the relevant user set.

    current_user_ratings = matrix.get(
        user_id
    )

    if not current_user_ratings:
        return []

    recommendations = defaultdict(float)

    # ==================================================
    # 9. Process each item the user liked
    # ==================================================

    for item_id, user_rating in current_user_ratings.items():

        # Only positively-rated items influence
        # collaborative recommendations.
        if user_rating < MIN_RATING_FOR_RECOMMENDATION:
            continue

        target_vector = centered_vectors.get(
            item_id
        )

        if not target_vector:
            continue

        target_users = target_vector.keys()

        # ==================================================
        # 10. Generate candidates using shared users
        # ==================================================

        candidates = build_candidate_common_users(
            target_item_id=item_id,
            target_users=target_users,
            user_item_index=user_item_index,
            rated_items=rated_items,
            min_common_users=MIN_COMMON_USERS,
        )

        # ==================================================
        # 11. Calculate cosine ONLY for valid candidates
        # ==================================================

        for other_item_id in candidates:

            other_vector = centered_vectors.get(
                other_item_id
            )

            if not other_vector:
                continue

            similarity = cosine_similarity(
                target_vector,
                other_vector,
                vector_norms[item_id],
                vector_norms[other_item_id],
                min_common_users=MIN_COMMON_USERS,
            )

            if similarity <= 0:
                continue

            # Same scoring idea as your original implementation.
            recommendations[other_item_id] += (
                similarity * user_rating
            )

    # ==================================================
    # 12. Rank
    # ==================================================

    ranked = sorted(
        recommendations.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    return ranked[:limit]


def get_collaborative_similar_items(
    db: Session,
    entertainment_id: int,
    limit: int = 20,
):
    """
    Return items similar to one entertainment item.

    Uses the same optimized candidate-generation approach.
    """

    matrix = build_rating_matrix(db)

    if not matrix:
        return []

    item_vectors = build_item_vectors(
        matrix
    )

    target_vector = item_vectors.get(
        entertainment_id
    )

    if not target_vector:
        return []

    user_averages = build_user_averages(
        matrix
    )

    centered_vectors = build_centered_vectors(
        item_vectors,
        user_averages,
    )

    vector_norms = build_vector_norms(
        centered_vectors
    )

    user_item_index = build_user_item_index(
        matrix
    )

    rated_items = {
        entertainment_id
    }

    candidates = build_candidate_common_users(
        target_item_id=entertainment_id,
        target_users=target_vector.keys(),
        user_item_index=user_item_index,
        rated_items=rated_items,
        min_common_users=MIN_COMMON_USERS,
    )

    similarities = []

    target_centered = centered_vectors[
        entertainment_id
    ]

    for item_id in candidates:

        other_vector = centered_vectors.get(
            item_id
        )

        if not other_vector:
            continue

        score = cosine_similarity(
            target_centered,
            other_vector,
            vector_norms[entertainment_id],
            vector_norms[item_id],
            min_common_users=MIN_COMMON_USERS,
        )

        if score <= 0:
            continue

        similarities.append(
            (item_id, score)
        )

    similarities.sort(
        key=lambda x: x[1],
        reverse=True,
    )

    return similarities[:limit]