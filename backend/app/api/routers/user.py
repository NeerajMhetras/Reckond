from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.user.user import UserResponse
from app.services.user_service import get_all_users_service,get_user_by_id
from app.core.security import get_current_user
from app.models.user.user import User


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserResponse])
async def get_all_users(
    db: Session = Depends(get_db)
):
    return get_all_users_service(db)

@router.get("/me", response_model=UserResponse)

async def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    return get_user_by_id(db, user_id)


