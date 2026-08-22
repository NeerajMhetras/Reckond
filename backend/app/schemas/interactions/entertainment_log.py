from datetime import datetime
from app.models.interactions.entertainment_log import LogAction
from pydantic import BaseModel, Field
from app.schemas.media.entertainment import MediaResponse

class EntertainmentLogCreate(BaseModel):
    entertainment_id: int
    action: LogAction
    logged_at: datetime


class EntertainmentLogResponse(BaseModel):
    id: int
    user_id: int
    entertainment_id: int
    action: LogAction
    logged_at: datetime
    created_at: datetime
    updated_at: datetime
    media: MediaResponse
class EntertainmentLogUpdate(BaseModel):
    action: LogAction | None = None
    logged_at: datetime | None = None