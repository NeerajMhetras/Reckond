from enum import Enum

from sqlalchemy import Column, Integer, String, Text, Date, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.database import Base


class MediaType(str, Enum):
    MOVIE = "movie"
    SERIES = "series"
    BOOK = "book"
    GAME = "game"


class Entertainment(Base):
    __tablename__ = "entertainment"

    __table_args__ = (UniqueConstraint("external_source","external_id",name="uq_entertainment_external_source_id"),)

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)

    description = Column(Text, nullable=True)

    poster_url = Column(String(500), nullable=True)

    backdrop_url = Column(String(500), nullable=True)

    release_date = Column(Date, nullable=True)

    media_type = Column(
        SQLEnum(MediaType),
        nullable=False
    )

    language = Column(String(50), nullable=True)

    external_id = Column(String(100), nullable=True)

    external_source = Column(String(50), nullable=True)

    movie_details = relationship("MovieDetails",back_populates="entertainment",uselist=False, cascade="all, delete-orphan")

    series_details = relationship("SeriesDetails",back_populates="entertainment",uselist=False, cascade="all, delete-orphan")

    game_details = relationship("GameDetails",back_populates="entertainment",uselist=False, cascade="all, delete-orphan")

    book_details = relationship("BookDetails",back_populates="entertainment",uselist=False, cascade = "all, delete-orphan")

    logs = relationship("EntertainmentLog",back_populates="entertainment",cascade="all, delete-orphan")

    watchlist = relationship("Watchlist", back_populates="entertainment",cascade="all, delete-orphan")

    ratings = relationship("Rating", back_populates="entertainment", cascade="all, delete-orphan")

    reviews = relationship("Review",back_populates="entertainment",cascade="all, delete-orphan")