import logging
from jose import JWTError

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.models.user import User
from app.core.auth import authenticate_user, create_access_token, decode_token
from app.core.config import settings

logger = logging.getLogger(__name__)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        """
        ログインボタンを押下した際の処理
        
        Parameters
        ----------
        request : Request
            リクエストオブジェクト
            
        Returns
        -------
        bool
            認証成功時はTrue、失敗時はFalse
        """
        form = await request.form()
        username, password = form["username"], form["password"]
        logger.debug(f"username: {username}, password: {password}")
        
        # ユーザー認証
        user = await authenticate_user(username, password)
        if not user:
            return False
            
        # JWTトークン生成
        access_token = create_access_token(data={"sub": username})
        
        # セッションにトークンを保存
        request.session["token"] = access_token
        
        return True

    async def logout(self, request: Request) -> bool:
        """ログアウトボタンを押下した際の処理"""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """
        認証処理（権限有無の確認）
        
        Parameters
        ----------
        request : Request
            リクエストオブジェクト
            
        Returns
        -------
        bool
            認証成功時はTrue、失敗時はFalse
        """
        token = request.session.get("token")
        if not token:
            return False
            
        try:
            # トークンのデコードと検証
            payload = decode_token(
                token,
                settings.jwt_secret_key,
                [settings.jwt_algorithm]
            )
            username = payload.get("sub")
            if not username:
                return False
                
            # ユーザーの存在確認
            user = await User.get_user_by_username(username)
            return user is not None
            
        except JWTError:
            return False
