from sqlalchemy import Column, Integer, String
from app.database.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    entertainment_logs = relationship("EntertainmentLog",back_populates="user",cascade="all, delete-orphan")
    watchlist = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review",back_populates="user",cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken",back_populates="user",cascade="all, delete-orphan")
    