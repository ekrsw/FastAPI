from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, String, Select
from typing import Optional

from .base import BaseDatabase
from app.db.session import AsyncContextManager
from app.schemas.user_schema import UserSchema


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class User(BaseDatabase):
    __tablename__ = "users"
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

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
        async with AsyncContextManager() as session:
            user_schema = UserSchema(username=username, password=plain_password)
            hashed_password = await cls.set_password(user_schema.password)
            new_user = cls(username=user_schema.username, hashed_password=hashed_password, is_admin=is_admin)
            session.add(new_user)
        return new_user
    
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
            result = await session.execute(Select(cls).where(cls.id == user_id))
            user = result.scalar_one_or_none()
        return user
    
    @classmethod
    async def get_user_by_username(cls, username: str):
        """ユーザー名からユーザーを取得する"""
        async with AsyncContextManager() as session:
            result = await session.execute(Select(cls).where(cls.username == username))
            user = result.scalar_one_or_none()
        return user
    
    @classmethod
    async def update_user(cls, user_id: int, username: str, is_admin: Optional[bool]=None):
        """ユーザー情報を更新する"""
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id)
            user.username = username
            user.is_admin = is_admin
            session.add(user)
    
    @classmethod
    async def delete_user(cls, user_id: int):
        """ユーザーを削除する"""
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id)
            await session.delete(user)
    
    @classmethod
    async def update_password(cls, user_id: int, plain_password: Optional[str]):
        """パスワードを更新する"""
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id)
            hashed_password = await cls.set_password(plain_password)
            user.hashed_password = hashed_password
            session.add(user)
