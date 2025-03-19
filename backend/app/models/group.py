from typing import Any, Dict, List, Type, Optional

from pydantic import BaseModel
from sqlalchemy import String, Select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ulid import new as ulid_new

from .base import ModelBaseMixinWithoutDeletedAt, T
from app.db.session import AsyncContextManager


class Group(ModelBaseMixinWithoutDeletedAt):
    __tablename__ = "groups"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"group_{str(ulid_new())}")
    groupname: Mapped[str] = mapped_column(String, nullable=False)

    operators = relationship("User", back_populates="group")

    def __str__(self):
        return self.groupname

    def __repr__(self):
        return self.groupname
    
    @classmethod
    async def create_group(cls: Type[T], *, obj_in: Dict[str, Any]) -> T:
        """グループ作成メソッド。

        AsyncContextManagerのコンテキスト終了時に暗黙的にcommitされます。

        Args:
            obj_in (Dict[str, Any]): 作成するグループの情報

        Returns:
            T: 作成されたグループオブジェクト（データベースにはまだcommitされていない状態）
        """
        async with AsyncContextManager() as session:
            new_group = cls()
            for field, value in obj_in.items():
                if hasattr(new_group, field):
                    setattr(new_group, field, value)
            session.add(new_group)
        return new_group
    
    @classmethod
    async def get_all_groups(cls: Type[T]) -> List[T]:
        """全てのグループを取得する。

        Returns:
            List[T]: 全てのグループのリスト
        """
        async with AsyncContextManager() as session:
            result = await session.execute(Select(cls))
            groups = result.scalars().all()
        return groups
    
    @classmethod
    async def get_group_by_id(cls: Type[T], group_id: int) -> Optional[T]:
        """IDによるグループ取得。

        Args:
            group_id (int): 取得するグループのID

        Returns:
            Optional[T]: 取得したグループオブジェクト。存在しない場合はNone
        """
        async with AsyncContextManager() as session:
            stmt = Select(cls).where(cls.id == group_id)
            result = await session.execute(stmt)
            group = result.scalars().first()
        return group
    
    @classmethod
    async def update_group(cls: Type[T], *, db_obj: T, obj_in: Dict[str, Any]) -> T:
        """グループ情報の更新。

        Args:
            db_obj (T): 更新対象のグループオブジェクト
            obj_in (Dict[str, Any]): 更新情報

        Returns:
            T: 更新後のグループオブジェクト
        """
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
        """グループの物理削除。

        指定されたIDのグループが存在しない場合は何も行いません。

        Args:
            group_id (int): 削除するグループのID
        """
        async with AsyncContextManager() as session:
            group = await cls.get_group_by_id(group_id)
            if group is not None:
                await session.delete(group)
                await session.commit()
    
    @classmethod
    async def from_schema(cls: Type[T], *, schema: BaseModel) -> T:
        """PydanticスキーマからGroupオブジェクトを作成。

        Args:
            schema (BaseModel): グループ情報を含むPydanticスキーマ

        Returns:
            T: 作成されたグループオブジェクト
        """
        schema_dict = schema.model_dump()
        return await cls.create_group(obj_in=schema_dict)


    @classmethod
    async def update_from_schema(cls: Type[T], *, db_obj: T, schema: BaseModel) -> T:
        """PydanticスキーマでGroupオブジェクトを更新。

        Args:
            db_obj (T): 更新対象のグループオブジェクト
            schema (BaseModel): 更新情報を含むPydanticスキーマ

        Returns:
            T: 更新後のグループオブジェクト

        Raises:
            ValueError: 更新対象のグループオブジェクトが存在しない場合
        """
        if db_obj is None:
            raise ValueError("Group not found")
        schema_dict = schema.model_dump(exclude_unset=True)
        return await cls.update_group(db_obj=db_obj, obj_in=schema_dict)
