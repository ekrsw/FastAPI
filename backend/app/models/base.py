import datetime

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class BaseDatabase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
