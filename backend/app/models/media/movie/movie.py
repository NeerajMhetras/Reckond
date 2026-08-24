from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class MovieDetails(Base):
    __tablename__ = "movie_details"

    id = Column(Integer, primary_key=True, index=True)

    entertainment_id = Column(
        Integer,
        ForeignKey("entertainment.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    runtime = Column(Integer, nullable=True)

    budget = Column(Integer, nullable=True)

    revenue = Column(Integer, nullable=True)

    entertainment = relationship(
        "Entertainment",
        back_populates="movie_details"
    )

    genres = relationship(
        "Genre",
        secondary="movie_genres",
        back_populates="movies"
    )

    keywords = relationship(
        "Keyword",
        secondary="movie_keywords",
        back_populates="movies"
    )

    cast = relationship(
        "MovieCast",
        back_populates="movie",
        cascade="all, delete-orphan"
    )

    crew = relationship(
        "MovieCrew",
        back_populates="movie",
        cascade="all, delete-orphan"
    )