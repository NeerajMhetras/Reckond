from app.database.database import SessionLocal
from app.recommendation.content_based import get_similar_media


db = SessionLocal()

results = get_similar_media(
    db=db,
    entertainment_id=2,
    limit=5
)

for result in results:

    media = result["media"]
    score = result["score"]

    print(
        media.title,
        "->",
        score
    )

db.close()