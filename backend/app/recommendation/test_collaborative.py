from app.database.database import SessionLocal
from app.recommendation.collaborative import (
    build_rating_matrix,
    build_item_vectors,
    build_user_averages,
    get_collaborative_similar_items,
)


db = SessionLocal()

try:
    matrix = build_rating_matrix(db)

    print("\n=== RATING MATRIX ===")
    for user_id, ratings in matrix.items():
        print(f"User {user_id}: {ratings}")

    user_averages = build_user_averages(matrix)

    print("\n=== USER AVERAGES ===")
    print(user_averages)

    item_vectors = build_item_vectors(matrix)

    print("\n=== ITEM VECTORS ===")
    for item_id, ratings in item_vectors.items():
        print(f"Item {item_id}: {ratings}")

    # Pick an item that actually has ratings
    entertainment_id = 113

    print(
        f"\n=== SIMILAR ITEMS TO {entertainment_id} ==="
    )

    recommendations = get_collaborative_similar_items(
        db,
        entertainment_id,
        limit=10
    )

    for item_id, score in recommendations:
        print(
            f"Item {item_id} -> similarity: {score:.4f}"
        )

finally:
    db.close()