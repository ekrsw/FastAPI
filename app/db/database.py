import datetime

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

class Database:
    def __init__(self):
        self.engine = create_async_engine(
            "sqlite+aiosqlite:///db.sqlite",
            connect_args={"check_same_thread": False},
        )
    
    async def init(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await self.connect_db()
    
    async def connect_db(self):
        async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        return async_session()

