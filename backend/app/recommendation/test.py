from app.database.database import SessionLocal
from app.models.media.entertainment import Entertainment
from app.recommendation.feature_builder import build_feature_text


db = SessionLocal()

for title in ["Inception", "Interstellar"]:

    media = (
        db.query(Entertainment)
        .filter(Entertainment.title == title)
        .first()
    )

    print("\n====================")
    print(title)
    print("====================")

    if media:
        print(build_feature_text(media))
    else:
        print("NOT FOUND")

db.close()