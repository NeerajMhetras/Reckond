from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database.database import Base


class MovieCast(Base):
    __tablename__ = "movie_cast"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    movie_id = Column(
        Integer,
        ForeignKey(
            "movie_details.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    person_id = Column(
        Integer,
        ForeignKey(
            "people.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    character = Column(
        String(255),
        nullable=True
    )

    cast_order = Column(
        Integer,
        nullable=True
    )

    movie = relationship(
        "MovieDetails",
        back_populates="cast"
    )

    person = relationship(
        "Person"
    )