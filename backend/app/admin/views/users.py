from typing import Any

from sqladmin import ModelView

from app.models.user import User


class UserAdminView(ModelView, model=User):  # type: ignore
    name_plural = "Users"
    column_list = "__all__"
    column_searchable_list = [User.id, User.username, User.is_admin]
    form_columns = [
        User.id,
        User.usernname,
        User.is_admin,
        User.hashed_password,
    ]
