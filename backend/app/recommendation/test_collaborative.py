from app.database.database import SessionLocal
from app.recommendation.collaborative import (
    get_collaborative_similar_items
)
from app.models.media.entertainment import Entertainment


db = SessionLocal()

entertainment_id = 2

results = get_collaborative_similar_items(
    db=db,
    entertainment_id=entertainment_id,
    limit=10
)

for item_id, score in results:

    media = (
        db.query(Entertainment)
        .filter(
            Entertainment.id == item_id
        )
        .first()
    )

    if media:
        print(
            media.title,
            "->",
            score
        )

db.close()