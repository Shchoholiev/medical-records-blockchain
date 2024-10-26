from fastapi import FastAPI

# Initialize FastAPI app
app = FastAPI()

# Simple route to say hello
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}