import logging

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

logger = logging.getLogger(__name__)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        """ログインボタンを押下した際の処理"""
        # フォームで入力したユーザ名とパスワードを取得
        form = await request.form()
        username, password = form["username"], form["password"]
        logger.debug(f"username: {username}, password: {password}")

        # ここに任意のチェック処理を記述
        # ...

        request.session["token"] = "dummy_token"

        return True

    async def logout(self, request: Request) -> bool:
        """ログアウトボタンを押下した際の処理"""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """認証処理（権限有無の確認）"""
        token = request.session.get("token")

        if not token:
            return False

        # ここに任意のチェック処理を記述
        # ...

        return True