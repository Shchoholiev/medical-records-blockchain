from freezegun import freeze_time
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from unittest.mock import patch
import os

def read_key_from_pem(file_path):
    with open(file_path, "r") as file:
        key = file.read()
    return key

PRIVATE_KEY = read_key_from_pem("private.pem")
PUBLIC_KEY = read_key_from_pem("public.pem")

ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

SAMPLE_DATA = {"user_id": "12345"}
EXPIRED_DATA = {"user_id": "expired_user"}

@pytest.fixture(scope="module", autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {"JWT_PRIVATE_KEY": PRIVATE_KEY, "JWT_PUBLIC_KEY": PUBLIC_KEY}):
        yield

def create_valid_token(data, expires_delta=None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    data.update({"exp": expire})
    return jwt.encode(data, PRIVATE_KEY, algorithm=ALGORITHM)

def test_create_access_token():
    from app.utils.jwt_handler import create_access_token

    with freeze_time("2024-10-27 12:00:00"):
        token = create_access_token(SAMPLE_DATA)
        decoded_data = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])

        assert decoded_data["user_id"] == SAMPLE_DATA["user_id"]

        expected_expiration = datetime(2024, 10, 27, 12, 30, 0, tzinfo=timezone.utc)
        assert datetime.fromtimestamp(decoded_data["exp"], timezone.utc) == expected_expiration

def test_create_access_token_with_custom_expiration():
    from app.utils.jwt_handler import create_access_token

    custom_expiration = timedelta(minutes=60)
    token = create_access_token(SAMPLE_DATA, expires_delta=custom_expiration)
    decoded_data = jwt.decode(token, PRIVATE_KEY, algorithms=[ALGORITHM])

    assert datetime.fromtimestamp(decoded_data["exp"], timezone.utc) > datetime.now(timezone.utc) + timedelta(minutes=59)

def test_verify_token_valid():
    from app.utils.jwt_handler import verify_token

    valid_token = create_valid_token(SAMPLE_DATA)
    payload = verify_token(valid_token)

    assert payload["user_id"] == SAMPLE_DATA["user_id"]

def test_verify_token_expired():
    from app.utils.jwt_handler import verify_token

    expired_token = create_valid_token(EXPIRED_DATA, expires_delta=timedelta(minutes=-1))

    with pytest.raises(ValueError, match="Invalid or expired token."):
        verify_token(expired_token)
