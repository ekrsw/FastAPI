import csv
import logging
from io import StringIO
from typing import Any, List, Tuple

from fastapi import Request, UploadFile
from fastapi.datastructures import UploadFile as FastAPIUploadFile  # 追加
from sqladmin import BaseView, expose

from app.models.user import User

logger = logging.getLogger(__name__)

DEFAULT_PASSWORD = "password123"


class UserCsvImportAdminView(BaseView):  # type: ignore
    name_plural = "ユーザーCSV一括登録"
    identity = "user_csv_import"
    methods = ["GET", "POST"]

    # 固定フィールドの定義
    REQUIRED_FIELDS = {
        "username": str,
        "password": str,
        "is_admin": bool,
        "group_id": str
    }

    # 除外フィールドの定義
    EXCLUDED_FIELDS = {
        "id", "hashed_password", "deleted_at",
        "created_at", "updated_at", "group"
    }

    # 動的フィールド取得メソッド
    def get_allowed_fields(self) -> dict:
        return {
            name: column.type.python_type
            for name, column in User.__table__.columns.items()
            if name not in self.EXCLUDED_FIELDS
        }

    # フィールド値のバリデーション
    def validate_field_value(self, field: str, value: Any, field_type: type) -> Any:
        if value is None or value == "":
            return None
        
        try:
            if field_type == bool:
                return str(value).lower() == 'true'
            return field_type(value)
        except (ValueError, TypeError):
            raise ValueError(f"{field}の値が不正です: {value}")

    async def process_csv_file(self, file: UploadFile) -> Tuple[int, int, List[str]]:
        """CSVファイルの処理
        
        Args:
            file (UploadFile): アップロードされたCSVファイル
        
        Returns:
            Tuple[int, int, List[str]]: 成功件数、エラー件数、エラー詳細のリスト
        """
        success_count = 0
        error_count = 0
        error_descriptions = []
        allowed_fields = self.get_allowed_fields()

        content = await file.read()
        content_str = content.decode('utf-8')
        csv_file = StringIO(content_str)
        reader = csv.DictReader(csv_file)

        for row in reader:
            try:
                # 必須フィールドのチェック
                if not row.get('username'):
                    error_count += 1
                    error_descriptions.append(f"行 {reader.line_num}: usernameは必須です")
                    continue

                # ユーザーデータの準備
                user_data = {
                    "username": row['username'],
                    "password": DEFAULT_PASSWORD,
                    "is_admin": str(row.get('is_admin', '')).lower() == 'true',
                    "group_id": row.get('group_id')
                }

                # 動的フィールドの処理
                for field, field_type in allowed_fields.items():
                    if field not in self.REQUIRED_FIELDS and field in row:
                        try:
                            value = self.validate_field_value(field, row[field], field_type)
                            if value is not None:
                                user_data[field] = value
                        except ValueError as e:
                            error_count += 1
                            error_descriptions.append(f"行 {reader.line_num}: {str(e)}")
                            continue

                # ユーザーの作成
                try:
                    await User.create_user(obj_in=user_data)
                    success_count += 1
                    logger.info(f"Successfully created user: {user_data['username']}")
                except Exception as e:
                    error_count += 1
                    error_msg = f"行 {reader.line_num}: ユーザー '{user_data['username']}' の作成に失敗しました - {str(e)}"
                    error_descriptions.append(error_msg)
                    logger.error(error_msg)

            except Exception as e:
                error_count += 1
                error_msg = f"行 {reader.line_num}: 予期せぬエラー - {str(e)}"
                error_descriptions.append(error_msg)
                logger.error(error_msg)

        return success_count, error_count, error_descriptions        

    @expose(f"/{identity}", methods=["GET", "POST"])
    async def user_csv_import(self, request: Request):
        """/user_csv_import のエンドポイント"""
        if request.method == "GET":
            return await self.templates.TemplateResponse(
                request,
                name=f"{self.identity}.html",
                context={"view": self},
            )

        # POSTリクエストの処理
        form = await request.form()
        files = form.getlist("files")

        logger.info(f"Received {len(files)} files")

        total_success = 0
        total_errors = 0
        all_error_descriptions = []

        # 各ファイルを処理
        for file in files:
            if not file.filename:  # ファイル名のチェックに変更
                logger.error(f"Invalid file object: {file}")
                continue

            if not file.filename.endswith('.csv'):
                total_errors += 1
                error_msg = f"ファイル '{file.filename}' はCSVファイルではありません"
                all_error_descriptions.append(error_msg)
                logger.error(error_msg)
                continue

            success_count, error_count, error_descriptions = await self.process_csv_file(file)
            total_success += success_count
            total_errors += error_count
            all_error_descriptions.extend(error_descriptions)

        logger.info(f"Total success: {total_success}, Total errors: {total_errors}")

        return await self.templates.TemplateResponse(
            request,
            name=f"{self.identity}.html",
            context={
                "view": self,
                "success_count": total_success,
                "error_count": total_errors,
                "error_descriptions": all_error_descriptions,
                "description": f"CSVファイルの処理が完了しました。{total_success}件のユーザーを作成しました。",
            },
        )
