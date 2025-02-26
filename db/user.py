from sqlalchemy import Column, String, Select
from .database import Database, BaseDatabase

class User(BaseDatabase):
    __tablename__ = "users"
    username = Column(String)

    @classmethod
    async def create_user(cls, username: str):
        db = Database()
        await db.init()
        session = await db.connect_db()
        session.add(cls(username=username))
        await session.commit()
        await session.close()
    
    @classmethod
    async def get_all_users(cls):
        db = Database()
        await db.init()
        session = await db.connect_db()
        result = await session.execute(Select(cls))
        await session.close()
        users = result.scalars().all()
        return users
    
    @classmethod
    async def get_user_by_id(cls, user_id: int):
        db = Database()
        await db.init()
        session = await db.connect_db()
        result = await session.execute(Select(cls).where(cls.id == user_id))
        user = result.scalar_one_or_none()
        await session.close()
        return user
        