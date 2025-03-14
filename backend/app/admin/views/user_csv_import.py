import csv
import logging
from io import StringIO
from typing import List, Tuple

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

        logger.info(f"Processing file: {file.filename}")

        # CSVファイルの内容を文字列として読み込み。
        content = await file.read()
        content_str = content.decode('utf-8')
        csv_file = StringIO(content_str)
        reader = csv.DictReader(csv_file)

        for row in reader:
            try:
                # usernameの必須チェック
                if not row.get('username'):
                    error_count += 1
                    error_descriptions.append(f"行 {reader.line_num}: usernameは必須です")
                    continue

                # is_adminの処理（デフォルトはFalse)
                is_admin_str = row.get('is_admin', '').lower()
                is_admin = is_admin_str == 'true'

                # ユーザーの作成
                username = row['username']
                logger.info(f"Creating user: {username}")
                try:
                    await User.create_user(
                        username=username,
                        plain_password=DEFAULT_PASSWORD,
                        is_admin=is_admin
                    )
                    success_count += 1
                    logger.info(f"Successfully created user: {username}")
                except Exception as e:
                    error_count += 1
                    error_msg = f"行 {reader.line_num}: ユーザー '{username}' の作成に失敗しました - {str(e)}"
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