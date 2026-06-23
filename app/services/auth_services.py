from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.logger import logger

from app.models.user_model import User
from app.schemas.user_schema import UserCreate
from app.auth import (
    hash_password,
    verify_password,
    create_access_token
)
from fastapi.security import OAuth2PasswordRequestForm

def create_user(user: UserCreate, db: Session):
    existing_user = db.query(User).filter(User.username == user.username).first()

    if existing_user:
        logger.warning("Signup attempted with existing username", extra={"username": user.username})
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info("New user created", extra={"username": user.username, "user_id": new_user.id})
    return new_user


def login_user(form_data: OAuth2PasswordRequestForm, db: Session):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
        logger.warning("Login failed — username not found", extra={"username": form_data.username})
        raise HTTPException(status_code=401, detail="Invalid username")

    if not verify_password(form_data.password, user.hashed_password):
        logger.warning("Login failed — wrong password", extra={"username": form_data.username})
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = create_access_token(data={"sub": user.username})
    logger.info("User logged in successfully", extra={"username": user.username})

    return {"access_token": access_token, "token_type": "bearer"}