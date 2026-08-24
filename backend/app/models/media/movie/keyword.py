from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Keyword(Base):
    __tablename__ = "keywords"

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
        secondary="movie_keywords",
        back_populates="keywords"
    )