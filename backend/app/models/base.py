import datetime

from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from typing import TypeVar

from app.db.database import Base


T = TypeVar('T', bound='BaseDatabase')

class ModelBaseMixin(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

class ModelBaseMixinWithoutDeletedAt(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
