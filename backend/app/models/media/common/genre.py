from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Genre(Base):
    __tablename__ = "genres"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    external_id = Column(
        Integer,
        nullable=False,
        unique=True
    )

    name = Column(
        String(100),
        nullable=False,
        unique=True
    )

    movies = relationship(
        "MovieDetails",
        secondary="movie_genres",
        back_populates="genres"
    )

    series = relationship(
        "SeriesDetails",
        secondary="series_genres",
        back_populates="genres"
    )