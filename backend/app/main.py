from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
import os

from app.models.user import User
from app.routers import auth, users
from app.core.config import settings
from app.db.database import Database


# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# lifespanコンテキストマネージャー
@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクルを管理します"""
    # 起動時の処理
    try:
        # データベース初期化
        db = Database()
        await db.init()
        logger.info("Database initialized successfully")
        
        # 初期管理者ユーザーの作成
        admin_username = settings.initial_admin_username
        admin_password = settings.initial_admin_password
        
        # 既存の管理者ユーザーを確認
        existing_admin = await User.get_user_by_username(admin_username)
        if not existing_admin:
            await User.create_user(
                username=admin_username,
                plain_password=admin_password,
                is_admin=True
            )
            logger.info(f"Initial admin user '{admin_username}' created successfully")
        else:
            logger.info(f"Admin user '{admin_username}' already exists")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    
    yield  # アプリケーションの実行中
    
    # 終了時の処理
    logger.info("Shutting down application")

# FastAPIアプリケーションの作成
app = FastAPI(
    title="FastAPI Backend",
    description="FastAPIを使用したバックエンドAPI",
    version="0.1.0",
    lifespan=lifespan,
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # フロントエンドのオリジン
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(users.router)
app.include_router(auth.router)

# ルートパスのエンドポイント
@app.get("/")
async def root():
    """APIのルートパスにアクセスした際の応答を返します"""
    return {
        "message": "Welcome to FastAPI Backend API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# アプリケーションの起動
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
