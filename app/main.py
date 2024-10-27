import logging
from fastapi import FastAPI, Depends
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")

from fastapi.security import OAuth2PasswordBearer
from app.api.blockchain_routes import router as blockchain_router
from app.auth.user_auth import router as auth_router
from app.auth.dependencies import get_current_user

logging.basicConfig(level=logging.INFO)
logging.getLogger('azure').setLevel(logging.WARNING)
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app.include_router(auth_router, prefix="/auth")

app.include_router(
    blockchain_router,
    prefix="/blocks",
    dependencies=[Depends(get_current_user)]  # Use JWT validation to protect the routes
)