from typing import Any

from sqladmin import ModelView
from starlette.requests import Request
from wtforms.validators import ValidationError
import wtforms

from app.models.user import User


class UserAdminView(ModelView, model=User):  # type: ignore
    name_plural = "Users"
    column_list = [User.id, User.username, User.is_admin, User.created_at, User.updated_at]
    column_searchable_list = [User.id, User.username, User.is_admin]
    column_sortable_list = [User.id, User.username, User.is_admin]
    column_filters = [User.id, User.username, User.is_admin, User.created_at, User.updated_at]
    form_columns = [
        User.username,
        User.is_admin,
        User.hashed_password,
    ]

    # パスワードラベルの変更
    column_labels = {User.hashed_password: "Password"}

    # フォームフィールドの上書き
    form_overrides = {"hashed_password": wtforms.PasswordField}

    # 更新時にパスワードを変更なし（空）で保存できるようにする
    form_args = {
        "render_kw": {"class": "form-control", "required": False},
        "validators": [wtforms.validators.Optional()],
    }

    async def insert_model(self, request: Request, data: dict) -> Any:
        if not data["hashed_password"]:
            raise ValidationError("Password is required.")
        return await super().insert_model(request, data)
    
    async def on_model_change(self, data: dict[str, Any], model: Any, is_created: bool, request: Request) -> None:
        if not is_created:
            if not data["hashed_password"]:
                data["hashed_password"] = model.hashed_password
                return
        # ハッシュ処理
        # Userクラスのset_passwordメソッドにてUserPasswordSchemaでValidationを行う
        data["hashed_password"] = await User.set_password(data["hashed_password"])
