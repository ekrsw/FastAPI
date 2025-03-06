from fastapi import FastAPI, HTTPException
from app.models.user import User


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello bbb"}

@app.post("/user/")
async def create_user(username: str, password: str, is_admin: bool=False):
    exit_user = await User.get_user_by_username(username)
    if exit_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = await User.create_user(username, password, is_admin)
    return new_user

@app.get("/user/{user_id}")
async def get_user_by_id(user_id: int):
    user = await User.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user