from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.database.database import Base


game_platforms = Table(
    "game_platforms",
    Base.metadata,

    Column(
        "game_id",
        ForeignKey("game_details.id", ondelete="CASCADE"),
        primary_key=True
    ),

    Column(
        "platform_id",
        ForeignKey("platforms.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class GameDetails(Base):
    __tablename__ = "game_details"

    id = Column(Integer, primary_key=True, index=True)

    entertainment_id = Column(
        Integer,
        ForeignKey("entertainment.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    entertainment = relationship(
        "Entertainment",
        back_populates="game_details"
    )

    platforms = relationship(
        "Platform",
        secondary=game_platforms,
        back_populates="games"
    )


class Platform(Base):
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(100),
        unique=True,
        nullable=False
    )

    games = relationship(
        "GameDetails",
        secondary=game_platforms,
        back_populates="platforms"
    )