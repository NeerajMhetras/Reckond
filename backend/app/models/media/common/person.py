from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Person(Base):
    __tablename__ = "people"

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
        String(255),
        nullable=False
    )