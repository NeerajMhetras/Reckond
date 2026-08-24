from pydantic import BaseModel

from app.models.media.series.series import SeriesType, AnimationType


class SeriesDetailsResponse(BaseModel):
    series_type: SeriesType
    animation_type: AnimationType | None = None
    number_of_seasons: int | None = None
    number_of_episodes: int | None = None