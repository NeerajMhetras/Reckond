from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.entertainment_log import EntertainmentLog
from app.models.entertainment import Entertainment
from app.models.user import User

from app.utils.media_serializer import build_media_response


def create_log(
    db: Session,
    user: User,
    entertainment_id: int,
    action,
    logged_at
):
    media = (
        db.query(Entertainment)
        .filter(
            Entertainment.id == entertainment_id
        )
        .first()
    )

    if not media:
        raise HTTPException(
            status_code=404,
            detail="Media not found"
        )

    log = EntertainmentLog(
        user_id=user.id,
        entertainment_id=entertainment_id,
        action=action,
        logged_at=logged_at
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return {
        "id": log.id,
        "user_id": log.user_id,
        "entertainment_id": log.entertainment_id,
        "action": log.action,
        "logged_at": log.logged_at,
        "created_at": log.created_at,
        "updated_at": log.updated_at,
        "media": build_media_response(
            log.entertainment
        )
    }

def get_logs(
    db: Session,
    user: User
):

    logs = (
        db.query(EntertainmentLog)
        .filter(
            EntertainmentLog.user_id == user.id
        )
        .order_by(
            EntertainmentLog.logged_at.desc()
        )
        .all()
    )

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "entertainment_id": log.entertainment_id,
            "action": log.action,
            "logged_at": log.logged_at,
            "created_at": log.created_at,
            "updated_at": log.updated_at,
            "media": build_media_response(
                log.entertainment
            )
        }
        for log in logs
    ]

def get_log(
    db: Session,
    user: User,
    log_id: int
):

    log = (
        db.query(EntertainmentLog)
        .filter(
            EntertainmentLog.id == log_id,
            EntertainmentLog.user_id == user.id
        )
        .first()
    )

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Entertainment log not found"
        )

    return {
        "id": log.id,
        "user_id": log.user_id,
        "entertainment_id": log.entertainment_id,
        "action": log.action,
        "logged_at": log.logged_at,
        "created_at": log.created_at,
        "updated_at": log.updated_at,
        "media": build_media_response(
            log.entertainment
        )
    }

def update_log(
    db: Session,
    user: User,
    log_id: int,
    action=None,
    logged_at=None
):

    log = (
        db.query(EntertainmentLog)
        .filter(
            EntertainmentLog.id == log_id,
            EntertainmentLog.user_id == user.id
        )
        .first()
    )

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Entertainment log not found"
        )

    if action is not None:
        log.action = action

    if logged_at is not None:
        log.logged_at = logged_at

    db.commit()
    db.refresh(log)

    return {
        "id": log.id,
        "user_id": log.user_id,
        "entertainment_id": log.entertainment_id,
        "action": log.action,
        "logged_at": log.logged_at,
        "created_at": log.created_at,
        "updated_at": log.updated_at,
        "media": build_media_response(
            log.entertainment
        )
    }

def delete_log(
    db: Session,
    user: User,
    log_id: int
):

    log = (
        db.query(EntertainmentLog)
        .filter(
            EntertainmentLog.id == log_id,
            EntertainmentLog.user_id == user.id
        )
        .first()
    )

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Entertainment log not found"
        )

    db.delete(log)
    db.commit()

    return {
        "message": "Entertainment log deleted successfully"
    }