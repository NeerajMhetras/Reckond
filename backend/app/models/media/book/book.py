from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.database.database import Base

book_authors = Table(
    "book_authors",
    Base.metadata,

    Column(
        "book_id",
        ForeignKey("book_details.id", ondelete="CASCADE"),
        primary_key=True
    ),

    Column(
        "author_id",
        ForeignKey("authors.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class BookDetails(Base):
    __tablename__ = "book_details"

    id = Column(Integer, primary_key=True, index=True)

    entertainment_id = Column(
        Integer,
        ForeignKey(
            "entertainment.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True
    )

    isbn = Column(String(20), nullable=True)

    pages = Column(Integer, nullable=True)

    publisher = Column(String(255), nullable=True)

    entertainment = relationship(
        "Entertainment",
        back_populates="book_details"
    )

    authors = relationship(
        "Author",
        secondary="book_authors",
        back_populates="books"
    )

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(255),
        nullable=False,
        unique=True
    )

    books = relationship(
        "BookDetails",
        secondary="book_authors",
        back_populates="authors"
    )