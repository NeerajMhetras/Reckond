from enum import Enum

from pydantic import BaseModel


class SeriesType(str, Enum):
    TV = "tv"
    ANIMATED = "animated"


class AnimationType(str, Enum):
    ANIME = "anime"
    WESTERN = "western"
    OTHER = "other"


class GenreResponse(BaseModel):
    id: int
    external_id: int
    name: str

    class Config:
        from_attributes = True


class KeywordResponse(BaseModel):
    id: int
    external_id: int
    name: str

    class Config:
        from_attributes = True


class PersonResponse(BaseModel):
    id: int
    external_id: int
    name: str

    class Config:
        from_attributes = True


class SeriesCastResponse(BaseModel):
    id: int
    person: PersonResponse
    character: str | None
    cast_order: int | None

    class Config:
        from_attributes = True


class SeriesCrewResponse(BaseModel):
    id: int
    person: PersonResponse
    department: str | None
    job: str | None

    class Config:
        from_attributes = True


class SeriesDetailsResponse(BaseModel):
    id: int
    entertainment_id: int

    series_type: SeriesType
    animation_type: AnimationType | None

    number_of_seasons: int | None
    number_of_episodes: int | None

    genres: list[GenreResponse]
    keywords: list[KeywordResponse]

    cast: list[SeriesCastResponse]
    crew: list[SeriesCrewResponse]

    class Config:
        from_attributes = True