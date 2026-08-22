from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.schemas.user.user import Token,UserCreate,UserResponse


from app.services.user_service import login_user,create_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
        "/",
        response_model=UserResponse
)

async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return create_user(db, user)

@router.post(
    "/login",
    response_model=Token
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return login_user(db, form_data)