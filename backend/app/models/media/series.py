from enum import Enum

from sqlalchemy import Column, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.database.database import Base


class SeriesType(str, Enum):
    TV = "tv"
    ANIMATED = "animated"

class AnimationType(str, Enum):
    ANIME = "anime"
    WESTERN = "western"
    OTHER = "other"


class SeriesDetails(Base):
    __tablename__ = "series_details"

    id = Column(Integer, primary_key=True, index=True)

    entertainment_id = Column(
        Integer,
        ForeignKey("entertainment.id",ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    series_type = Column(
        SQLEnum(SeriesType),
        nullable=False
    )

    animation_type = Column(
        SQLEnum(AnimationType),
        nullable=True
    )
    
    number_of_seasons = Column(Integer, nullable=True)

    number_of_episodes = Column(Integer, nullable=True)

    entertainment = relationship(
        "Entertainment",
        back_populates="series_details"
    )