from sqlalchemy import Column, String, Select
from .database import BaseDatabase, AsyncContextManager

class User(BaseDatabase):
    __tablename__ = "users"
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    
    @classmethod
    async def create_user(cls, username: str):
        async with AsyncContextManager() as session:
            session.add(cls(username=username))
    
    @classmethod
    async def get_all_users(cls):
        async with AsyncContextManager() as session:
            result = await session.execute(Select(cls))
            users = result.scalars().all()
            return users

    @classmethod
    async def get_user_by_id(cls, user_id: int):
        async with AsyncContextManager() as session:
            result = await session.execute(Select(cls).where(cls.id == user_id))
            user = result.scalar_one_or_none()
            return user
    
    @classmethod
    async def get_user_by_username(cls, username: str):
        async with AsyncContextManager() as session:
            result = await session.execute(Select(cls).where(cls.username == username))
            user = result.scalar_one_or_none()
            return user
    
    @classmethod
    async def update_user(cls, user_id: int, username: str):
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id)
            user.username = username
            session.add(user)
    
    @classmethod
    async def delete_user(cls, user_id: int):
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id)
            await session.delete(user)
