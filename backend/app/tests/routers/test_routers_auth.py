from httpx import AsyncClient
import pytest
from jose import jwt

from app.models.user import User
from app.core.config import settings
from app.tests.conftest import test_admin, test_user, unique_username, client


@pytest.mark.asyncio
async def test_login_for_access_token_success(client: AsyncClient):
    """
    正しい認証情報を使用してアクセストークンとリフレッシュトークンを取得できることを確認します。
    """
    # テストユーザーの作成
    username = "testuser"
    password = "testpassword"
    new_user = await User.create_user(username=username, plain_password=password)

    # /auth/token エンドポイントにリクエストを送信
    response = await client.post(
        "/auth/token",
        data={"username": username, "password": password}
    )

    assert response.status_code == 200, f"トークン取得に失敗しました: {response.text}"
    tokens = response.json()
    assert "access_token" in tokens, "レスポンスに access_token が含まれていません"
    assert tokens["token_type"] == "bearer", "トークンタイプが正しくありません"
    assert "refresh_token" in tokens, "レスポンスに refresh_token が含まれていません"

    # アクセストークンのデコードと検証
    access_token = tokens["access_token"]
    payload = jwt.decode(access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    assert payload.get("sub") == username, "アクセストークンのペイロードが正しくありません"
