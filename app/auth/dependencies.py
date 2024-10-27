from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.utils.jwt_handler import verify_token

# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Extract and verify the JWT token to get the current user.
    
    Args:
        token (str): JWT token from the Authorization header.
    
    Returns:
        dict: The user claims extracted from the token, including user_id, roles, and validator_id.
    
    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        payload = verify_token(token)
        
        if "user_id" not in payload or "roles" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user data.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload 

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    Extract the user ID from the JWT token.
    
    Args:
        token (str): JWT token from the Authorization header.
    
    Returns:
        str: The user_id extracted from the token.
    
    Raises:
        HTTPException: If the token is invalid or does not contain the user_id.
    """
    user = await get_current_user(token)
    return user.get("user_id")

async def get_current_validator_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    Extract the validator ID from the JWT token.
    
    Args:
        token (str): JWT token from the Authorization header.
    
    Returns:
        str: The validator_id extracted from the token.
    
    Raises:
        HTTPException: If the token is invalid or does not contain the validator_id.
    """
    user = await get_current_user(token)
    return user.get("validator_id")

async def get_current_user_roles(token: str = Depends(oauth2_scheme)) -> list:
    """
    Extract the user roles from the JWT token.
    
    Args:
        token (str): JWT token from the Authorization header.
    
    Returns:
        list: A list of roles extracted from the token.
    
    Raises:
        HTTPException: If the token is invalid or does not contain the roles.
    """
    user = await get_current_user(token)
    return user.get("roles", [])
