from pydantic import BaseModel


class BookDetailsResponse(BaseModel):
    isbn: str | None = None
    pages: int | None = None
    publisher: str | None = None
    authors: list[str] = []