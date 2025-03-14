import logging

from fastapi import Request
from sqladmin import BaseView, expose

logger = logging.getLogger(__name__)


class UserCsvImportAdminView(BaseView):  # type: ignore
    name_plural = "ユーザーCSV一括登録"
    identity = "user_csv_import"
    methods = ["GET", "POST"]

    @expose(f"/{identity}", methods=["GET", "POST"])
    async def user_csv_import(self, request: Request):
        """/user_csv_import のエンドポイント"""
        # GETとPOSTで処理を分ける
        if request.method == "GET":
            # HTMLをJinja2テンプレートを使って作成してレスポンス
            # HTMLの作成に必要な情報はcontextにdictで渡す
            return await self.templates.TemplateResponse(
                request,
                name=f"{self.identity}.html",
                context={"view": self},
            )
        elif request.method == "POST":
            # CSVインポート処理を記述

            # HTMLをJinja2テンプレートを使って作成してレスポンス
            return await self.templates.TemplateResponse(
                request,
                name=f"{self.identity}.html",
                context={
                    "view": self,
                    "success_count": 1,
                    "error_count": 0,
                    "description": "ダミーレスポンスです",
                },
            )