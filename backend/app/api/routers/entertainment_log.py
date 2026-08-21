from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.core.security import get_current_user

from app.models.user import User

from app.schemas.entertainment_log import (
    EntertainmentLogCreate,
    EntertainmentLogResponse,
    EntertainmentLogUpdate
)

from app.services.entertainment_log_service import (
    create_log,
    get_logs,
    get_log,
    update_log,
    delete_log
)


router = APIRouter(
    prefix="/logs",
    tags=["Entertainment Logs"]
)


@router.post(
    "/",
    response_model=EntertainmentLogResponse
)
async def create_entertainment_log(
    request: EntertainmentLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_log(
        db=db,
        user=current_user,
        entertainment_id=request.entertainment_id,
        action=request.action,
        logged_at=request.logged_at
    )


@router.get(
    "/",
    response_model=list[EntertainmentLogResponse]
)
async def get_user_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_logs(
        db=db,
        user=current_user
    )


@router.get(
    "/{log_id}",
    response_model=EntertainmentLogResponse
)
async def get_entertainment_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_log(
        db=db,
        user=current_user,
        log_id=log_id
    )


@router.put(
    "/{log_id}",
    response_model=EntertainmentLogResponse
)
async def update_entertainment_log(
    log_id: int,
    request: EntertainmentLogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return update_log(
        db=db,
        user=current_user,
        log_id=log_id,
        action=request.action,
        logged_at=request.logged_at
    )


@router.delete(
    "/{log_id}"
)
async def delete_entertainment_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_log(
        db=db,
        user=current_user,
        log_id=log_id
    )