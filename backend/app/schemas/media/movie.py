from pydantic import BaseModel

from pydantic import BaseModel


class GenreResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class KeywordResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class PersonResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class MovieCastResponse(BaseModel):
    person: PersonResponse
    character: str | None
    cast_order: int | None

    class Config:
        from_attributes = True

class MovieCrewResponse(BaseModel):
    person: PersonResponse
    department: str | None
    job: str | None

    class Config:
        from_attributes = True

class MovieDetailsResponse(BaseModel):
    runtime: int | None
    budget: int | None
    revenue: int | None

    genres: list[GenreResponse]
    keywords: list[KeywordResponse]
    cast: list[MovieCastResponse]
    crew: list[MovieCrewResponse]

    class Config:
        from_attributes = True

    