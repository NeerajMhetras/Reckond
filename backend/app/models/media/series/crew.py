from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database.database import Base


class SeriesCrew(Base):
    __tablename__ = "series_crew"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    series_id = Column(
        Integer,
        ForeignKey(
            "series_details.id",
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

    series = relationship(
        "SeriesDetails",
        back_populates="crew"
    )

    person = relationship(
        "Person"
    )