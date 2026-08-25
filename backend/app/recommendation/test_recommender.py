from app.recommendation.recommender import recommend_for_user
from app.database.database import SessionLocal

db = SessionLocal()

results = recommend_for_user(
    db=db,
    user_id=1,
    limit=10
)

for result in results:
    print(
        result["media"].title,
        "->",
        result["score"]
    )