from pydantic import BaseModel

class MovieDetailsResponse(BaseModel):
    runtime: int | None
    budget: int | None
    revenue: int | None

    