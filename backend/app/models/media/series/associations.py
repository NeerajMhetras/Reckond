from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Table
)

from app.database.database import Base


series_genres = Table(
    "series_genres",
    Base.metadata,

    Column(
        "series_id",
        ForeignKey(
            "series_details.id",
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


series_keywords = Table(
    "series_keywords",
    Base.metadata,

    Column(
        "series_id",
        ForeignKey(
            "series_details.id",
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