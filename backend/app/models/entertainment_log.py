from datetime import datetime

from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Enum as SQLEnum
)

from sqlalchemy.orm import relationship

from app.database.database import Base


class LogAction(str, Enum):
    WATCHED = "watched"
    READ = "read"
    PLAYED = "played"
    COMPLETED = "completed"


class EntertainmentLog(Base):
    __tablename__ = "entertainment_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    entertainment_id = Column(
        Integer,
        ForeignKey(
            "entertainment.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    action = Column(
        SQLEnum(LogAction),
        nullable=False
    )

    logged_at = Column(
        DateTime,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="entertainment_logs"
    )

    entertainment = relationship(
        "Entertainment",
        back_populates="logs"
    )