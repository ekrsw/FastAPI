from fastapi import FastAPI, HTTPException
from app.models.user import User

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello bbb"}

@app.post("/users/")
async def create_user(username: str, password: str, is_admin: bool=False):
    exit_user = await User.get_user_by_username(username)
    if exit_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = await User.create_user(username, password, is_admin)
    return new_user