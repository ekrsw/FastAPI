from fastapi import FastAPI, HTTPException
from app.models.user import User

from app.routers import users, auth


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello bbb"}

@app.get("/user/{user_id}")
async def get_user_by_id(user_id: int):
    user = await User.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ルーターの登録
app.include_router(users.router)
app.include_router(auth.router)
