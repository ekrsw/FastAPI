from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, String, Select
from typing import Optional
from .base import BaseDatabase
from db.session import AsyncContextManager


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class User(BaseDatabase):
    __tablename__ = "users"
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    async def valify_password(self, plain_password: str) -> bool:
        """入力されたパスワードがハッシュと一致するかを確かめる"""
        return pwd_context.verify(plain_password, self.hashed_password)
    
    @staticmethod
    async def set_password(plain_password: str) -> str:
        """パスワードをハッシュ化して返す"""
        return pwd_context.hash(plain_password)
    
    @classmethod
    async def create_user(cls, username: str, plain_password: Optional[str]=None, is_admin: Optional[bool]=False):
        """ユーザーを作成する"""
        # ユーザーが既に存在する場合はHTTP 400エラーを返す
        async with AsyncContextManager() as session:
            result = await session.execute(Select(cls).where(cls.username == username))
            user = result.scalar_one_or_none()
            if user is not None:
                raise HTTPException(status_code=400, detail=f"`{username}` already exists")
            hashed_password = await cls.set_password(plain_password)
            session.add(cls(username=username, hashed_password=hashed_password, is_admin=is_admin))
    
    @classmethod
    async def get_all_users(cls):
        """全てのユーザーを取得する"""
        async with AsyncContextManager() as session:
            result = await session.execute(Select(cls))
            users = result.scalars().all()
            return users

    @classmethod
    async def get_user_by_id(cls, user_id: int):
        """ユーザーIDからユーザーを取得する"""
        async with AsyncContextManager() as session:
            # `is_admin`が空欄の場合はHTTP 400エラーを返す
            result = await session.execute(Select(cls).where(cls.id == user_id))
            user = result.scalar_one_or_none()
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return user
    
    @classmethod
    async def get_user_by_username(cls, username: str):
        """ユーザー名からユーザーを取得する"""
        async with AsyncContextManager() as session:
            result = await session.execute(Select(cls).where(cls.username == username))
            user = result.scalar_one_or_none()
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return user
    
    @classmethod
    async def update_user(cls, user_id: int, username: str, is_admin: Optional[bool]=None):
        """ユーザー情報を更新する"""
        # `is_admin`が空欄の場合はHTTP 400エラーを返す
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id)
            user.username = username
            if is_admin is not None:
                user.is_admin = is_admin
            else:
                raise HTTPException(status_code=400, detail="is_admin is required")
            session.add(user)
    
    @classmethod
    async def delete_user(cls, user_id: int):
        """ユーザーを削除する"""
        # ユーザーが存在しない場合はHTTP 404エラーを返す
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            await session.delete(user)
    
    @classmethod
    async def update_password(cls, user_id: int, plain_password: Optional[str]):
        """パスワードを更新する"""
        # ユーザーが存在しない場合はHTTP 404エラーを返す
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            hashed_password = await cls.set_password(plain_password)
            user.hashed_password = hashed_password
            session.add(user)
