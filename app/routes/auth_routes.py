from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user_model import User
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.auth import verify_token
from app.auth import (
    hash_password,
    verify_password,
    create_access_token
)


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


# Database dependency
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

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

    return user

@router.post("/signup")
def signup(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):

    # Check if username already exists
    existing_user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Hash the password
    hashed_pw = hash_password(password)

    # Create new user object
    new_user = User(
        username=username,
        hashed_password=hashed_pw
    )

    # Save into database
    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "username": new_user.username
    }

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username"
        )

    if not verify_password(
        form_data.password,
        user.hashed_password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    access_token = create_access_token(
        data={"sub": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
def read_current_user(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "username": current_user.username
    }