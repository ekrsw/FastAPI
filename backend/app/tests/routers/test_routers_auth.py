from httpx import AsyncClient
import pytest
from jose import jwt

from app.models.user import User
from app.core.config import settings
from app.tests.conftest import test_admin, test_user, unique_username, client


@pytest.mark.asyncio
async def test_login_for_access_token_success(test_user, client: AsyncClient):
    """
    正しい認証情報を使用してアクセストークンとリフレッシュトークンを取得できることを確認します。
    """
    # テストユーザーの作成
    user, password = test_user

    # /auth/token エンドポイントにリクエストを送信
    response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )

    assert response.status_code == 200, f"トークン取得に失敗しました: {response.text}"
    tokens = response.json()
    assert "access_token" in tokens, "レスポンスに access_token が含まれていません"
    assert tokens["token_type"] == "bearer", "トークンタイプが正しくありません"
    assert "refresh_token" in tokens, "レスポンスに refresh_token が含まれていません"

    # アクセストークンのデコードと検証
    access_token = tokens["access_token"]
    payload = jwt.decode(access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    assert payload.get("sub") == user.username, "アクセストークンのペイロードが正しくありません"

@pytest.mark.asyncio
async def test_login_for_access_token_invalid_credentials(client: AsyncClient):
    """
    無効な認証情報でトークン取得が失敗することを確認します。
    """
    # 存在しないユーザーでリクエストを送信
    response = await client.post(
        "/auth/token",
        data={"username": "invaliduser", "password": "invalidpassword"}
    )

    assert response.status_code == 401, "無効な認証情報で 401 エラーが返されるべきです"
    assert response.json()["detail"] == "Incorrect username or password", "エラーメッセージが正しくありません"

@pytest.mark.asyncio
async def test_refresh_access_token_success(test_user, client: AsyncClient):
    """
    正しいリフレッシュトークンを使用して新しいアクセストークンを取得できることを確認します。
    """
    # テストユーザーの作成
    user, password = test_user

    # トークン取得
    response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    tokens = response.json()
    refresh_token = tokens["refresh_token"]

    # /auth/refresh エンドポイントにリクエストを送信
    response = await client.post(
        "/auth/refresh",
        headers={"Refresh-Token": refresh_token}
    )

    assert response.status_code == 200, f"アクセストークンのリフレッシュに失敗しました: {response.text}"
    new_tokens = response.json()
    assert "access_token" in new_tokens, "レスポンスに新しい access_token が含まれていません"
    assert new_tokens["token_type"] == "bearer", "トークンタイプが正しくありません"

    # 新しいアクセストークンのデコードと検証
    access_token = new_tokens["access_token"]
    payload = jwt.decode(access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    assert payload.get("sub") == user.username, "新しいアクセストークンのペイロードが正しくありません"

@pytest.mark.asyncio
async def test_refresh_access_token_invalid_token(client: AsyncClient):
    """
    無効なリフレッシュトークンでアクセストークンのリフレッシュが失敗することを確認します。
    """
    # 無効なリフレッシュトークンを使用
    response = await client.post(
        "/auth/refresh",
        headers={"Refresh-Token": "invalidtoken"}
    )

    assert response.status_code == 401, "無効なリフレッシュトークンで 401 エラーが返されるべきです"
    assert response.json()["detail"] == "Invalid refresh token", "エラーメッセージが正しくありません"

@pytest.mark.asyncio
async def test_access_protected_route_with_token(test_user, client: AsyncClient):
    """
    取得したアクセストークンを使用して保護されたエンドポイントにアクセスできることを確認します。
    """
    # テストユーザーの作成
    user, password = test_user

    # トークン取得
    response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    tokens = response.json()
    access_token = tokens["access_token"]

    # 保護されたエンドポイントにアクセス
    response = await client.get(
        f"/users/name/{user.username}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200, f"保護されたエンドポイントへのアクセスに失敗しました: {response.text}"
    data = response.json()
    assert data["username"] == user.username, "取得したユーザー名が正しくありません"