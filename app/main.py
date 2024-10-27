from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")

# Initialize FastAPI app
app = FastAPI()

# Simple route to say hello
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}