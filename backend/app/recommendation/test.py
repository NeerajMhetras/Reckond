from app.database.database import SessionLocal
from app.recommendation.content_based import get_similar_media


db = SessionLocal()

for entertainment_id in [2, 3, 4]:

    print("\n======================")
    print("ENTERTAINMENT:", entertainment_id)
    print("======================")

    results = get_similar_media(
        db=db,
        entertainment_id=entertainment_id,
        limit=10
    )

    if not results:
        print("NO SIMILAR ITEMS")

    for result in results:
        print(
            result["media"].id,
            result["media"].title,
            "->",
            result["score"]
        )

db.close()