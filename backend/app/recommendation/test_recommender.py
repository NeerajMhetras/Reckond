# from app.recommendation.recommender import recommend_for_user
# from app.database.database import SessionLocal

# db = SessionLocal()

# results = recommend_for_user(
#     db=db,
#     user_id=1,
#     limit=10
# )

# for result in results:
#     print(
#         result["media"].title,
#         "->",
#         result["score"]
#     )

from app.database.database import SessionLocal
from app.models.interactions.rating import Rating
from app.models.interactions.entertainment_log import EntertainmentLog
from app.recommendation.recommender import recommend_for_user


db = SessionLocal()

user_id = 1

ratings = (
    db.query(Rating)
    .filter(Rating.user_id == user_id)
    .all()
)

logs = (
    db.query(EntertainmentLog)
    .filter(EntertainmentLog.user_id == user_id)
    .all()
)

print("RATINGS:")
for rating in ratings:
    print(
        rating.entertainment_id,
        rating.rating
    )

print("\nLOGS:")
for log in logs:
    print(
        log.entertainment_id
    )

print("\nRECOMMENDATIONS:")

results = recommend_for_user(
    db=db,
    user_id=user_id,
    limit=10
)

if not results:
    print("NO RECOMMENDATIONS")

for result in results:
    print(
        result["media"].title,
        "->",
        result["score"]
    )

db.close()