import datetime
from typing import Any

from sqlalchemy import event, Integer, DateTime, orm, String
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.sql import func
from typing import TypeVar

from app.db.database import Base


T = TypeVar('T', bound='BaseDatabase')

class ModelBaseMixin(Base):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

class ModelBaseMixinWithoutDeletedAt(Base):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

@event.listens_for(Session, "do_orm_execute")
def _add_filtering_deleted_at(execute_state: Any) -> None:
    """論理削除用のfilterを自動的に適用する
    以下のようにすると、論理削除済のデータも含めて取得可能
    select(...).filter(...).execution_options(include_deleted=True).
    
    論理削除されていないレコードのみ取得
    db.query(User).all()
    
    論理削除済みのレコードも含めて取得
    db.query(User).execution_options(include_deleted=True).all()
    """
    if (
        execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.is_relationship_load
        and not execute_state.execution_options.get("include_deleted", False)
    ):
        execute_state.statement = execute_state.statement.options(
            orm.with_loader_criteria(  # ignore[mypy]
                ModelBaseMixin,
                lambda cls: cls.deleted_at.is_(None),
                include_aliases=True,
            ),
        )