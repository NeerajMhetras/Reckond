from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    entertainment_id = Column(
        Integer,
        ForeignKey("entertainment.id", ondelete="CASCADE"),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="reviews"
    )

    entertainment = relationship(
        "Entertainment",
        back_populates="reviews"
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "entertainment_id",
            name="uq_user_entertainment_review"
        ),
    )