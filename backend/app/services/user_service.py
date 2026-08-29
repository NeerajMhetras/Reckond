from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user.user import User
from app.schemas.user.user import UserCreate,UserLogin
from app.core.security import hash_password,verify_password,create_access_token,create_refresh_token,decode_refresh_token


def create_user(db: Session, user: UserCreate):

    existing_email = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    existing_username = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password)
    )
    try:

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="User already exists"
        )

def get_all_users_service(db: Session):
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

def login_user(db: Session, form_data: OAuth2PasswordRequestForm):
    

    email = form_data.username.strip().lower()
    
    db_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    if not verify_password(
        form_data.password,
        db_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(
        data={
            "sub": str(db_user.id)
        }
    )

    refresh_token = create_refresh_token(
        data={
            "sub": str(db_user.id)
        }
    )
    return{
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

def refresh_access_token(refresh_token: str):

    user_id = decode_refresh_token(
        refresh_token
    )

    access_token = create_access_token(
        data={
            "sub": str(user_id)
        }
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }