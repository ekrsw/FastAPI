from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
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

# FastAPIアプリケーションの作成
app = FastAPI(
    title="FastAPI Backend",
    description="FastAPIを使用したバックエンドAPI",
    version="0.1.0",
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(users.router)
app.include_router(auth.router)

# データベース初期化
@app.on_event("startup")
async def startup_db_client():
    """アプリケーション起動時にデータベースを初期化します"""
    try:
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

@app.on_event("shutdown")
async def shutdown_db_client():
    """アプリケーション終了時の処理"""
    logger.info("Shutting down application")

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
