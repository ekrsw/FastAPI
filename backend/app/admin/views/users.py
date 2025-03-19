from typing import Any

from sqladmin import ModelView
from sqlalchemy import ClauseElement, Select
from starlette.requests import Request
from wtforms.validators import ValidationError
import wtforms

from app.models.user import User


class UserAdminView(ModelView, model=User):  # type: ignore
    name_plural = "ユーザー"
    # ここにフィールドを追加
    column_list = [
        User.id,
        User.username,
        User.fullname,
        User.is_admin,
        "group.groupname",
        User.deleted_at,
        User.created_at,
        User.updated_at
        ]
    column_searchable_list = [
        User.id,
        User.username,
        User.fullname,
        User.is_admin
        ]
    column_sortable_list = [
        User.id,
        User.username,
        User.fullname,
        User.is_admin,
        User.deleted_at
        ]
    
    # ここにフィールドを追加
    form_columns = [
        User.username,
        User.fullname,
        User.is_admin,
        User.hashed_password,
        User.group_id,
        User.deleted_at
    ]

    # パスワードラベルの変更とその他のラベル
    column_labels = {
        User.id: "ID",
        User.username: "ユーザー名",
        User.fullname: "フルネーム",
        User.is_admin: "管理者",
        "group.groupname": "グループ名",
        User.deleted_at: "削除日時",
        User.created_at: "作成日時",
        User.updated_at: "更新日時",
        User.hashed_password: "Password"
    }

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
    
    async def _run_query(self, stmt: ClauseElement) -> Any:
        """論理削除されたレコードも含めて出力するようにクエリを実行する

        Usersテーブルは削除時に論理削除ができるようにdeleted_atカラムを持っているため、管理画面では論理削除されたレコードも表示できるようにする
        論理削除を使用しない場合は_run_queryメソッドをオーバーライドする必要はないため、このメソッドを削除しても問題ない

        """
        if isinstance(stmt, Select):
            # include_deleted=Trueを指定することで論理削除されたレコードも含めて出力する
            stmt = stmt.execution_options(include_deleted=True)
        return await super()._run_query(stmt)

    form_include_pk = True

