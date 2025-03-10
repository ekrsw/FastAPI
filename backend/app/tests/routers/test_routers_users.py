from httpx import AsyncClient
import pytest
from jose import jwt

from app.models.user import User
from app.core.config import settings
from app.tests.conftest import test_admin, test_user, unique_username, client


@pytest.mark.asyncio
async def test_read_user_by_id_success(test_user, client: AsyncClient):
    """
    正しい認証情報と存在するユーザーIDで、ユーザー情報を取得できることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # /users/{user_id} エンドポイントにリクエストを送信
    response = await client.get(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 200, f"ユーザー情報の取得に失敗しました: {response.text}"
    data = response.json()
    assert data["id"] == user.id, "取得したユーザーIDが正しくありません"
    assert data["username"] == user.username, "取得したユーザー名が正しくありません"
    assert data["is_admin"] == user.is_admin, "取得した管理者権限が正しくありません"

@pytest.mark.asyncio
async def test_read_user_by_id_not_found(test_user, client: AsyncClient):
    """
    存在しないユーザーIDを指定した場合に404エラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # 存在しないユーザーIDでリクエストを送信
    non_existent_id = 99999
    response = await client.get(
        f"/users/{non_existent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 404, "存在しないユーザーIDで404エラーが返されるべきです"
    assert response.json()["detail"] == "User not found", "エラーメッセージが正しくありません"

@pytest.mark.asyncio
async def test_read_user_by_id_unauthorized(client: AsyncClient):
    """
    認証なしでアクセスした場合に401エラーが返されることを確認します。
    """
    # 認証なしでリクエストを送信
    response = await client.get("/users/1")

    # レスポンスの検証
    assert response.status_code == 401, "認証なしのアクセスで401エラーが返されるべきです"
    assert response.json()["detail"] == "Not authenticated", "エラーメッセージが正しくありません"

@pytest.mark.asyncio
async def test_read_user_by_username_success(test_user, client: AsyncClient):
    """
    正しい認証情報と存在するユーザー名で、ユーザー情報を取得できることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # /users/name/{username} エンドポイントにリクエストを送信
    response = await client.get(
        f"/users/name/{user.username}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 200, f"ユーザー情報の取得に失敗しました: {response.text}"
    data = response.json()
    assert data["id"] == user.id, "取得したユーザーIDが正しくありません"
    assert data["username"] == user.username, "取得したユーザー名が正しくありません"
    assert data["is_admin"] == user.is_admin, "取得した管理者権限が正しくありません"

@pytest.mark.asyncio
async def test_read_user_by_username_not_found(test_user, client: AsyncClient):
    """
    存在しないユーザー名を指定した場合に404エラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # 存在しないユーザー名でリクエストを送信
    non_existent_username = "non_existent_user"
    response = await client.get(
        f"/users/name/{non_existent_username}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 404, "存在しないユーザー名で404エラーが返されるべきです"
    assert response.json()["detail"] == "User not found", "エラーメッセージが正しくありません"


@pytest.mark.asyncio
async def test_read_user_by_username_unauthorized(client: AsyncClient):
    """
    認証なしでアクセスした場合に401エラーが返されることを確認します。
    """
    # 認証なしでリクエストを送信
    response = await client.get("/users/name/testuser")

    # レスポンスの検証
    assert response.status_code == 401, "認証なしのアクセスで401エラーが返されるべきです"
    assert response.json()["detail"] == "Not authenticated", "エラーメッセージが正しくありません"

@pytest.mark.asyncio
async def test_read_all_users_success(test_user, client: AsyncClient):
    """
    認証済みユーザーが全てのユーザー情報を取得できることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # 追加のテストユーザーを作成
    additional_user = await User.create_user(
        username="additional_test_user",
        plain_password="test_password123",
        is_admin=False
    )
    
    # /auth/token エンドポイントでアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # /users エンドポイントにリクエストを送信
    response = await client.get(
        "/users/",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 200, f"ユーザー情報の取得に失敗しました: {response.text}"
    data = response.json()
    
    # レスポンスが配列であることを確認
    assert isinstance(data, list), "レスポンスは配列であるべきです"
    
    # 2人のユーザーが存在することを確認
    assert len(data) == 2, "取得したユーザー数が正しくありません"
    
    # テストユーザーとadditional_userの情報が含まれていることを確認
    user_ids = [u["id"] for u in data]
    assert user.id in user_ids, "テストユーザーの情報が含まれていません"
    assert additional_user.id in user_ids, "追加のテストユーザーの情報が含まれていません"

@pytest.mark.asyncio
async def test_read_all_users_unauthorized(client: AsyncClient):
    """
    認証なしでアクセスした場合に401エラーが返されることを確認します。
    """
    # 認証なしでリクエストを送信
    response = await client.get("/users/")

    # レスポンスの検証
    assert response.status_code == 401, "認証なしのアクセスで401エラーが返されるべきです"
    assert response.json()["detail"] == "Not authenticated", "エラーメッセージが正しくありません"


@pytest.mark.asyncio
async def test_read_all_users_empty(test_user, client: AsyncClient):
    """
    認証済みユーザーが自分以外のユーザーが存在しない状態でユーザー一覧を取得できることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]
    
    # 全てのユーザーを削除（テストユーザーは除く）
    users = await User.get_all_users()
    for u in users:
        if u.id != user.id:  # テストユーザーは削除しない
            await User.delete_user(u.id)

    # /users エンドポイントにリクエストを送信
    response = await client.get(
        "/users/",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 200, "認証済みユーザーは空のリストを取得できるべきです"
    data = response.json()
    assert isinstance(data, list), "レスポンスは配列であるべきです"
    assert len(data) == 1, "テストユーザーのみが存在するべきです"
    assert data[0]["id"] == user.id, "テストユーザーの情報が正しくありません"