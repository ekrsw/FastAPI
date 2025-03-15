from typing import List, Optional, Dict, Any, Type, TypeVar, Union
from passlib.context import CryptContext

from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Boolean, Column, String, Select
from sqlalchemy.ext.hybrid import hybrid_property

from .base import BaseDatabase, T
from app.db.session import AsyncContextManager
from app.schemas.user_schema import UserSchema, UserPasswordSchema


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class User(BaseDatabase):
    __tablename__ = "users"
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

    async def verify_password(self, plain_password: str) -> bool:
        """入力されたパスワードがハッシュと一致するかを確かめる"""
        return pwd_context.verify(plain_password, self.hashed_password)
    
    @staticmethod
    async def set_password(plain_password: str) -> str:
        """パスワードをハッシュ化して返す"""
        cleaned_password = UserPasswordSchema(password=plain_password).password
        return pwd_context.hash(cleaned_password)
    
    @classmethod
    async def create_user(cls: Type[T], *, obj_in: Dict[str, Any]) -> T:
        """ユーザーを作成する"""
        async with AsyncContextManager() as session:
            user_schema = UserSchema(**obj_in)
            hashed_password = await cls.set_password(user_schema.password)
            new_user = cls(username=user_schema.username, hashed_password=hashed_password, is_admin=user_schema.is_admin)
            session.add(new_user)
        return new_user
    
    @classmethod
    async def get_all_users(cls: Type[T]):
        """全てのユーザーを取得する"""
        async with AsyncContextManager() as session:
            result = await session.execute(Select(cls))
            users = result.scalars().all()
        return users

    @classmethod
    async def get_user_by_id(cls: Type[T], user_id: int):
        """ユーザーIDからユーザーを取得する"""
        async with AsyncContextManager() as session:
            result = await session.execute(Select(cls).where(cls.id == user_id))
            user = result.scalar_one_or_none()
        return user
    
    @classmethod
    async def get_user_by_username(cls: Type[T], username: str):
        """ユーザー名からユーザーを取得する"""
        async with AsyncContextManager() as session:
            result = await session.execute(Select(cls).where(cls.username == username))
            user = result.scalar_one_or_none()
        return user
    
    '''
    @classmethod
    async def update_user(cls: Type[T], user_id: int, username: str, is_admin: Optional[bool]=None):
        """ユーザー情報を更新する"""
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id)
            user.username = username
            if is_admin is not None:  # is_adminがNoneでない場合のみ更新
                user.is_admin = is_admin
            session.add(user)'''
    
    # 仮
    @classmethod
    async def update_user(cls: Type[T], *, db_obj: T, obj_in: Dict[str, Any]) -> T:
        """汎用ユーザー情報を更新する"""
        async with AsyncContextManager() as session:
            # 現在のデータを取得
            obj_data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
            
            # パスワードを特別に処理
            if "password" in obj_in:
                hashed_password = await cls.set_password(obj_in["password"])
                del obj_in["password"]
                update_data = {**obj_in, "hashed_password": hashed_password}
            else:
                update_data = obj_in.copy()
            
            # 動的にフィールドを更新
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            session.add(db_obj)
        return db_obj
    
    @classmethod
    async def delete_user(cls: Type[T], user_id: int):
        """ユーザーを削除する"""
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id)
            await session.delete(user)
    
    @classmethod
    async def update_password(cls: Type[T], user_id: int, plain_password: Optional[str]):
        """パスワードを更新する"""
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id)
            hashed_password = await cls.set_password(plain_password)
            user.hashed_password = hashed_password
            session.add(user)
    
    @classmethod
    async def create_or_update_user(cls: Type[T], user_id: int, username: str, plain_password: str, is_admin: bool = False):
        """ユーザーを作成または更新する"""
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id)
            if user:
                # 既存ユーザーの更新
                user.username = username
                user.is_admin = is_admin
                hashed_password = await cls.set_password(plain_password)
                user.hashed_password = hashed_password
                session.add(user)
                create_or_update = True
                new_or_updated_user = user # 更新されたユーザー
            else:
                # 新規ユーザーの作成
                user_schema = UserSchema(username=username, password=plain_password)
                hashed_password = await cls.set_password(user_schema.password)
                new_user = cls(id=user_id, username=user_schema.username, hashed_password=hashed_password, is_admin=is_admin)
                session.add(new_user)
                create_or_update = False
                new_or_updated_user = new_user # 新規作成されたユーザー
        return new_or_updated_user, create_or_update
    
    # Pydanticモデルとの連携用メソッド
    @classmethod
    async def from_schema(cls: Type[T], *, schema: BaseModel) -> T:
        """PydanticスキーマからUserオブジェクトを作成"""
        schema_dict = schema.dict()
        return cls.create_user(obj_in=schema_dict)
    
    @classmethod
    async def update_from_schema(cls: Type[T], *, db_obj: T, schema: BaseModel) -> T:
        """PydanticスキーマでUserオブジェクトを更新"""
        schema_dict = schema.dict(exclude_unset=True)
        return await cls.update_user(db_obj=db_obj, obj_in=schema_dict)
        

