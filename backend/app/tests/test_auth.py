import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from app.main import app
from app.core.config import settings
from app.models.user import User


@pytest.fixture
def client():
    """テスト用のクライアントを作成する"""
    return TestClient(app)


@pytest_asyncio.fixture
async def test_user():
    """テスト用のユーザーを作成する"""
    # テスト用のユーザーが存在するか確認
    user = await User.get_user_by_username("testuser")
    if user:
        return user
    
    # テスト用のユーザーを作成
    user = await User.create_user(
        username="testuser",
        plain_password="testpassword",
        is_admin=False
    )
    return user


@pytest_asyncio.fixture
async def test_admin():
    """テスト用の管理者ユーザーを作成する"""
    # テスト用の管理者ユーザーが存在するか確認
    admin = await User.get_user_by_username("testadmin")
    if admin:
        return admin
    
    # テスト用の管理者ユーザーを作成
    admin = await User.create_user(
        username="testadmin",
        plain_password="testadminpassword",
        is_admin=True
    )
    return admin


@pytest.mark.asyncio
async def test_create_token(client, test_user):
    """トークン作成のテスト"""
    response = client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "testpassword",
            "grant_type": "password",
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"
    
    # トークンの検証
    payload = jwt.decode(
        token_data["access_token"],
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )
    assert payload["sub"] == "testuser"


@pytest.mark.asyncio
async def test_invalid_login(client):
    """無効なログイン情報でのテスト"""
    response = client.post(
        "/auth/token",
        data={
            "username": "nonexistentuser",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.asyncio
async def test_get_me(client, test_user):
    """現在のユーザー情報取得のテスト"""
    # まずトークンを取得
    response = client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "testpassword",
            "grant_type": "password",
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
    )
    token_data = response.json()
    
    # トークンを使用してユーザー情報を取得
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token_data['access_token']}"}
    )
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == "testuser"
    assert user_data["is_admin"] is False


@pytest.mark.asyncio
async def test_refresh_token(client, test_user):
    """トークンリフレッシュのテスト"""
    # まずトークンを取得
    response = client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "testpassword",
            "grant_type": "password",
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
    )
    token_data = response.json()
    
    # リフレッシュトークンを使用して新しいトークンを取得
    response = client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {token_data['access_token']}"}
    )
    assert response.status_code == 200
    new_token_data = response.json()
    assert "access_token" in new_token_data
    assert "refresh_token" in new_token_data
    assert new_token_data["token_type"] == "bearer"
    
    # 新しいトークンが古いトークンと異なることを確認
    assert new_token_data["access_token"] != token_data["access_token"]
    assert new_token_data["refresh_token"] != token_data["refresh_token"]


@pytest.mark.asyncio
async def test_unauthorized_access(client):
    """認証なしでのアクセスのテスト"""
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
