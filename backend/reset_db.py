from sqlalchemy import text

from app.database.database import engine, Base

# Import all models so SQLAlchemy knows about them
from app.models.user.user import User
from app.models.media.entertainment import Entertainment
from app.models.interactions.watchlist import Watchlist
from app.models.interactions.rating import Rating
from app.models.interactions.review import Review
from app.models.interactions.entertainment_log import EntertainmentLog
# import your other models too


with engine.connect() as connection:

    connection.execute(
        text("DROP SCHEMA public CASCADE")
    )

    connection.execute(
        text("CREATE SCHEMA public")
    )

    connection.commit()


Base.metadata.create_all(bind=engine)

print("Database reset successfully.")