from sqlalchemy import Column, Integer, ForeignKey, Table

from app.database.database import Base


movie_genres = Table(
    "movie_genres",
    Base.metadata,

    Column(
        "movie_id",
        ForeignKey(
            "movie_details.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    ),

    Column(
        "genre_id",
        ForeignKey(
            "genres.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )
)


movie_keywords = Table(
    "movie_keywords",
    Base.metadata,

    Column(
        "movie_id",
        ForeignKey(
            "movie_details.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    ),

    Column(
        "keyword_id",
        ForeignKey(
            "keywords.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )
)