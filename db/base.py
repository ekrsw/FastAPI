import datetime

from sqlalchemy import Column, Integer, DateTime
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

class AsyncContextManager:
    async def __aenter__(self):
        db = Database()
        await db.init()
        self.session = await db.connect_db()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            # エラーが発生した場合はロールバック、そうでなければコミット
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            # 最後にセッションをクローズ
            await self.session.close()

class BaseDatabase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
