from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import ModelBaseMixinWithoutDeletedAt


class Group(ModelBaseMixinWithoutDeletedAt):
    __tablename__ = "groups"
    groupname: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        return f"<Group {self.groupname}>"
    
    