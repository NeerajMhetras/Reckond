from sqlalchemy import text

from app.database.database import engine, Base

# Import all models so SQLAlchemy knows about them
from app.models.user import User
from app.models.entertainment import Entertainment
from app.models.watchlist import Watchlist
from app.models.rating import Rating
from app.models.review import Review
from app.models.entertainment_log import EntertainmentLog
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