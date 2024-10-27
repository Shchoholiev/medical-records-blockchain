from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

from pydantic import BaseModel
from app.utils.jwt_handler import create_access_token
from app.services.user_service import UserService

router = APIRouter()
user_service = UserService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(login_data: LoginRequest):
    """
    Authenticate a user and generate a JWT token.

    Args:
        login_data (LoginRequest): The JSON data containing email and password.

    Returns:
        dict: Access token and token type.
    """
    user = user_service.verify_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "roles": user.roles,
            "validator_id": user.validator_id
        },
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
