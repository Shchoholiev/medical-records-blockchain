from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import os

PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY")
PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY")

if not PRIVATE_KEY or not PUBLIC_KEY:
    raise ValueError("JWT keys are missing. Ensure JWT_PRIVATE_KEY and JWT_PUBLIC_KEY are set in the environment.")

ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT token using the private key for RS256 algorithm.
    
    Args:
        data (dict): Data to be encoded in the token.
        expires_delta (Optional[timedelta]): Expiration time for the token.
    
    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, PRIVATE_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """
    Verify a JWT token using the public key for RS256 algorithm.
    
    Args:
        token (str): The JWT token to be verified.
    
    Returns:
        dict: The payload data if the token is valid.
    
    Raises:
        JWTError: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid or expired token.")
