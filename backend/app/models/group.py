from typing import Any, Dict, List, Type

from pydantic import BaseModel
from sqlalchemy import Integer, String, Select
from sqlalchemy.orm import Mapped, mapped_column

from .base import ModelBaseMixinWithoutDeletedAt, T
from app.db.session import AsyncContextManager


class Group(ModelBaseMixinWithoutDeletedAt):
    __tablename__ = "groups"
    groupname: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        return f"<Group {self.groupname}>"
    
    @classmethod
    async def create_group(cls: Type[T], *, obj_in: Dict[str, Any]) -> T:
        """グループ作成メソッド"""
        async with AsyncContextManager() as session:
            new_group = cls()
            for field, value in obj_in.items():
                if hasattr(new_group, field):
                    setattr(new_group, field, value)
            session.add(new_group)
        return new_group
    
    @classmethod
    async def get_all_groups(cls: Type[T]) -> List[T]:
        """全てのグループを取得する"""
        async with AsyncContextManager() as session:
            result = await session.execute(Select(cls))
            groups = result.scalars().all()
        return groups
    
    @classmethod
    async def get_group_by_id(cls: Type[T], group_id: int) -> T:
        """IDによるグループ取得"""
        async with AsyncContextManager() as session:
            result = await session.execute(Select(cls)).where(cls.id == group_id)
            group = result.scalars().first()
        return group
    
    @classmethod
    async def update_group(cls: Type[T], *, db_obj: T, obj_in: Dict[str, Any]) -> T:
        """グループ情報の更新"""
        async with AsyncContextManager() as session:
            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
        return db_obj
    
    @classmethod
    async def delete_group_permanently(cls: Type[T], group_id: int) -> None:
        """グループの物理削除"""
        async with AsyncContextManager() as session:
            group = await cls.get_user_by_id(group_id)
            session.delete(group)
            await session.commit()
    
    @classmethod
    async def from_schema(cls: Type[T], *, schema: BaseModel) -> T:
        """PydanticスキーマからGroupオブジェクトを作成"""
        schema_dict = schema.model_dump()
        return await cls.create_group(obj_in=schema_dict)


    @classmethod
    async def update_from_schema(cls: Type[T], *, db_obj: T, schema: BaseModel) -> T:
        """PydanticスキーマでGroupオブジェクトを更新"""
        if db_obj is None:
            raise ValueError("Group not found")
        schema_dict = schema.model_dump(exclude_unset=True)
        return await cls.update_group(db_obj=db_obj, obj_in=schema_dict)