from sqlalchemy import Column, String
from .database import Database, BaseDatabase

class User(BaseDatabase):
    __tablename__ = "users"
    username = Column(String)

    @classmethod
    async def add_user(cls, username: str):
        async with Database().connect_db() as session:
            session.add(cls(username=username))
            await session.commit()
    