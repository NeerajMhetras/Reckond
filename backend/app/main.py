from fastapi import FastAPI
from sqlalchemy import text
from app.database.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.routers.user import router as user_router
from app.api.routers.entertainment_log import router as entertainment_log_router
from app.api.routers.media import router as entertainment_router
from app.api.routers.watchlist import router as watchlist_router
from app.api.routers.rating import router as rating_router
from app.api.routers.review import router as review_router
from app.api.routers.recommendation import router as recommendation_router

from app.models.user.user import User
from app.models.media.entertainment import Entertainment
from app.models.media.movie.movie import MovieDetails
from app.models.media.series.series import SeriesDetails
from app.models.media.game.game import GameDetails,Platform
from app.models.media.book.book import BookDetails, Author
from app.models.interactions.entertainment_log import EntertainmentLog
from app.models.interactions.watchlist import Watchlist
from app.models.interactions.rating import Rating
from app.models.interactions.review import Review


app = FastAPI(
    title = "Unified Entertainment Platform API",
    version = "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router)
app.include_router(entertainment_log_router)
app.include_router(entertainment_router)
app.include_router(auth_router)
app.include_router(watchlist_router)
app.include_router(rating_router)
app.include_router(review_router)
app.include_router(recommendation_router)

Base.metadata.create_all(bind=engine)



@app.get("/")
async def root():
   return {"message": "Backend running"}

