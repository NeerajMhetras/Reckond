from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database.database import Base


class MovieCrew(Base):
    __tablename__ = "movie_crew"

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

    department = Column(
        String(100),
        nullable=True
    )

    job = Column(
        String(100),
        nullable=True
    )

    movie = relationship(
        "MovieDetails",
        back_populates="crew"
    )

    person = relationship(
        "Person"
    )