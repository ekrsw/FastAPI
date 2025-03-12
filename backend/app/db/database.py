import datetime
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


# 環境変数からDATABASE_URLを取得するか、設定から構築する
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.database_user}:"
    f"{settings.database_password}@{settings.database_host}:"
    f"{settings.database_port}/{settings.database_name}"
)

Base = declarative_base()

class Database:
    def __init__(self):
        """非同期エンジンの作成, セッションの作成"""
        self.engine = create_async_engine(
            DATABASE_URL,
            echo=True,
        )
        self.async_session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
    
    async def init(self):
        """データベースの初期化"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await self.connect_db()
    
    async def connect_db(self):
        """非同期セッションの作成"""
        return self.async_session_factory

    def get_session_factory(self):
        """セッションファクトリーの取得。awaitする必要なし"""
        return self.async_session_factory