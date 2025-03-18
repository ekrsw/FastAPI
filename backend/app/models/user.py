from typing import Any, Dict, Optional, List, Type, TypeVar, Union
from passlib.context import CryptContext

from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Boolean, String, Select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import ModelBaseMixin, T
from app.db.session import AsyncContextManager
from app.schemas.user_schema import UserCreate, UserUpdate, UserPasswordSchema


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class User(ModelBaseMixin):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # ここにフィールドを追加

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
        """ユーザー作成メソッド"""
        async with AsyncContextManager() as session:
            if "password" in obj_in:
                hashed_password = await cls.set_password(obj_in["password"])
                del obj_in["password"]
                obj_data = {**obj_in, "hashed_password": hashed_password}
            else:
                obj_data = obj_in.copy()
            
            new_user = cls()
            for field, value in obj_data.items():
                if hasattr(new_user, field):
                    setattr(new_user, field, value)
            session.add(new_user)
        return new_user


    @classmethod
    async def get_all_users(cls: Type[T], include_deleted: bool = False) -> List[T]:
        """全てのユーザーを取得する"""
        async with AsyncContextManager() as session:
            stmt = Select(cls)
            if include_deleted:
                stmt = stmt.execution_options(include_deleted=True)
            result = await session.execute(stmt)
            users = result.scalars().all()
        return users

    @classmethod
    async def get_user_by_id(cls: Type[T], user_id: str, include_deleted: bool = False) -> T:
        """ユーザーIDからユーザーを取得する
        
        Parameters
        ----------
        user_id : str
        ユーザーID
        include_deleted : bool, default False
        論理削除済みのユーザーも含めて取得するかどうか
        
        Returns
        -------
        User
        取得したユーザー
        """
        async with AsyncContextManager() as session:
            stmt = Select(cls).where(cls.id == user_id)
            if include_deleted:
                stmt = stmt.execution_options(include_deleted=True)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
        return user
    
    @classmethod
    async def get_user_by_username(cls: Type[T], username: str, include_deleted: bool = False):
        """ユーザー名からユーザーを取得する"""
        async with AsyncContextManager() as session:
            stmt = Select(cls).where(cls.username == username)
            if include_deleted:
                stmt = stmt.execution_options(include_deleted=True)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
        return user
    
    @classmethod
    async def update_user(cls: Type[T], *, db_obj: T, obj_in: Dict[str, Any]) -> T:
        """
        汎用ユーザー情報を更新する
        
        Parameters
        ----------
        db_obj : User
            更新対象のユーザーオブジェクト
        obj_in : Dict[str, Any]
            更新情報
        
        Returns
        -------
        User
            更新後のユーザーオブジェクト
        
        Raises
        ------
        ValueError
            更新対象のユーザーオブジェクトが存在しない場合
        Exception
            論理削除済みのユーザーを更新しようとした場合
        """
        async with AsyncContextManager() as session:
            # 最新のユーザー情報を取得して削除状態を確認
            current_user = await cls.get_user_by_id(db_obj.id, include_deleted=True)
            if current_user is None:
                raise ValueError("User not found")
            if current_user.deleted_at is not None:
                raise Exception("Cannot update deleted user")

            # パスワードを特別に処理
            update_data = obj_in.copy()
            if "password" in update_data:
                hashed_password = await cls.set_password(update_data["password"])
                del update_data["password"]
                update_data["hashed_password"] = hashed_password
            
            # 動的にフィールドを更新
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
        return db_obj
    
    @classmethod
    async def delete_user(cls: Type[T], user_id: str):
        """ユーザーを削除する"""
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id, include_deleted=True)
            user.deleted_at = func.now()
            session.add(user)
            await session.commit()
    
    @classmethod
    async def delete_user_permanently(cls: Type[T], user_id: str):
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id, include_deleted=True)
            await session.delete(user)
            await session.commit()
    
    @classmethod
    async def update_password(cls: Type[T], user_id: str, plain_password: Optional[str]):
        """パスワードを更新する"""
        async with AsyncContextManager() as session:
            user = await cls.get_user_by_id(user_id)
            hashed_password = await cls.set_password(plain_password)
            user.hashed_password = hashed_password
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user
    
    # Pydanticモデルとの連携用メソッド
    @classmethod
    async def from_schema(cls: Type[T], *, schema: BaseModel) -> T:
        """PydanticスキーマからUserオブジェクトを作成"""
        schema_dict = schema.model_dump()
        return await cls.create_user(obj_in=schema_dict)
    
    @classmethod
    async def update_from_schema(cls: Type[T], *, db_obj: T, schema: BaseModel) -> T:
        """PydanticスキーマでUserオブジェクトを更新"""
        if db_obj is None:
            raise ValueError("User not found")
        schema_dict = schema.model_dump(exclude_unset=True)
        return await cls.update_user(db_obj=db_obj, obj_in=schema_dict)
