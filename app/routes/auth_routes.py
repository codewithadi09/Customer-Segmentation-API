from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.logger import logger
from app.database import SessionLocal
from app.models.user_model import User
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.auth import verify_token
from app.auth import (
    hash_password,
    verify_password,
    create_access_token
)
from app.schemas.user_schema import UserCreate, UserResponse
from app.dependencies import get_db
from app.services.auth_services import create_user, login_user


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


# Database dependency
'''def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
        '''

# Dependency to get current logged-in user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    username = verify_token(token)

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    logger.info("Auth check passed", extra={"username": user.username})

    return user

@router.post(
    "/signup",
    response_model=UserResponse
)
def signup(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    return create_user(user, db)
     

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    return login_user(
        form_data=form_data,
        db=db
    )

@router.get(
    "/me",
    response_model=UserResponse
)
def read_current_user(
    current_user: User = Depends(get_current_user)
):

    return current_user


