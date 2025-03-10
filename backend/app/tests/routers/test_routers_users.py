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

@pytest.mark.asyncio
async def test_update_user_self_success(test_user, client: AsyncClient):
    """
    一般ユーザーが自分自身の情報を更新できることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # 新しいユーザー名
    new_username = f"updated_{user.username}"
    
    # /users/{user_id} エンドポイントにPUTリクエストを送信
    response = await client.put(
        f"/users/{user.id}",
        json={"username": new_username},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 200, f"ユーザー情報の更新に失敗しました: {response.text}"
    data = response.json()
    assert data["id"] == user.id, "更新したユーザーIDが正しくありません"
    assert data["username"] == new_username, "ユーザー名が更新されていません"
    assert data["is_admin"] == user.is_admin, "管理者権限が変更されています"

@pytest.mark.asyncio
async def test_update_user_by_admin_success(test_admin, test_user, client: AsyncClient):
    """
    管理者が他のユーザーの情報を更新できることを確認します。
    """
    # 管理者ユーザーとテストユーザーの作成
    admin, admin_password = test_admin
    user, _ = test_user
    
    # 管理者のアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": admin.username, "password": admin_password}
    )
    access_token = token_response.json()["access_token"]

    # 新しいユーザー名
    new_username = f"admin_updated_{user.username}"
    
    # 管理者が一般ユーザーの情報を更新
    response = await client.put(
        f"/users/{user.id}",
        json={"username": new_username},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 200, f"管理者によるユーザー情報の更新に失敗しました: {response.text}"
    data = response.json()
    assert data["id"] == user.id, "更新したユーザーIDが正しくありません"
    assert data["username"] == new_username, "ユーザー名が更新されていません"
    assert data["is_admin"] == user.is_admin, "管理者権限が変更されています"

@pytest.mark.asyncio
async def test_update_user_admin_privilege_success(test_admin, test_user, client: AsyncClient):
    """
    管理者が他のユーザーの管理者権限を変更できることを確認します。
    """
    # 管理者ユーザーとテストユーザーの作成
    admin, admin_password = test_admin
    user, _ = test_user
    
    # 管理者のアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": admin.username, "password": admin_password}
    )
    access_token = token_response.json()["access_token"]

    # 一般ユーザーを管理者に昇格
    response = await client.put(
        f"/users/{user.id}",
        json={"username": user.username, "is_admin": True},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 200, f"管理者権限の変更に失敗しました: {response.text}"
    data = response.json()
    assert data["id"] == user.id, "更新したユーザーIDが正しくありません"
    assert data["username"] == user.username, "ユーザー名が変更されています"
    assert data["is_admin"] == True, "管理者権限が更新されていません"

@pytest.mark.asyncio
async def test_update_user_not_found(test_user, client: AsyncClient):
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
    response = await client.put(
        f"/users/{non_existent_id}",
        json={"username": "new_username"},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 404, "存在しないユーザーIDで404エラーが返されるべきです"
    assert response.json()["detail"] == "User not found", "エラーメッセージが正しくありません"

@pytest.mark.asyncio
async def test_update_other_user_forbidden(test_user, client: AsyncClient):
    """
    一般ユーザーが他のユーザーの情報を更新しようとした場合に403エラーが返されることを確認します。
    """
    # 2人のテストユーザーを作成
    user1, password1 = test_user
    user2 = await User.create_user(
        username="another_test_user",
        plain_password="test_password123",
        is_admin=False
    )
    
    # user1のアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user1.username, "password": password1}
    )
    access_token = token_response.json()["access_token"]

    # user1がuser2の情報を更新しようとする
    response = await client.put(
        f"/users/{user2.id}",
        json={"username": "new_username"},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 403, "他のユーザーの情報更新で403エラーが返されるべきです"
    assert "Not enough permissions" in response.json()["detail"], "エラーメッセージが正しくありません"

@pytest.mark.asyncio
async def test_update_admin_privilege_forbidden(test_user, client: AsyncClient):
    """
    一般ユーザーが管理者権限を変更しようとした場合に403エラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # 自分自身を管理者に昇格しようとする
    response = await client.put(
        f"/users/{user.id}",
        json={"username": user.username, "is_admin": True},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 403, "管理者権限の変更で403エラーが返されるべきです"
    assert "Only admins can change admin privileges" in response.json()["detail"], "エラーメッセージが正しくありません"

@pytest.mark.asyncio
async def test_update_user_unauthorized(client: AsyncClient):
    """
    認証なしでアクセスした場合に401エラーが返されることを確認します。
    """
    # 認証なしでリクエストを送信
    response = await client.put(
        "/users/1",
        json={"username": "new_username"}
    )

    # レスポンスの検証
    assert response.status_code == 401, "認証なしのアクセスで401エラーが返されるべきです"
    assert response.json()["detail"] == "Not authenticated", "エラーメッセージが正しくありません"


@pytest.mark.asyncio
async def test_delete_user_by_admin_success(test_admin, test_user, client: AsyncClient):
    """
    管理者が他のユーザーを削除できることを確認します。
    """
    # 管理者ユーザーとテストユーザーの作成
    admin, admin_password = test_admin
    user, _ = test_user
    
    # 管理者のアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": admin.username, "password": admin_password}
    )
    access_token = token_response.json()["access_token"]

    # 管理者が一般ユーザーを削除
    response = await client.delete(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 200, f"ユーザーの削除に失敗しました: {response.text}"
    data = response.json()
    assert data["message"] == "User deleted successfully", "削除成功メッセージが正しくありません"
    
    # 削除されたユーザーが存在しないことを確認
    deleted_user = await User.get_user_by_id(user.id)
    assert deleted_user is None, "ユーザーが削除されていません"

@pytest.mark.asyncio
async def test_delete_user_not_found(test_admin, client: AsyncClient):
    """
    存在しないユーザーIDを指定した場合に404エラーが返されることを確認します。
    """
    # 管理者ユーザーの作成とアクセストークンの取得
    admin, admin_password = test_admin
    
    # 管理者のアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": admin.username, "password": admin_password}
    )
    access_token = token_response.json()["access_token"]

    # 存在しないユーザーIDでリクエストを送信
    non_existent_id = 99999
    response = await client.delete(
        f"/users/{non_existent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 404, "存在しないユーザーIDで404エラーが返されるべきです"
    assert response.json()["detail"] == "User not found", "エラーメッセージが正しくありません"

@pytest.mark.asyncio
async def test_delete_user_forbidden(test_user, client: AsyncClient):
    """
    一般ユーザーがユーザーを削除しようとした場合に403エラーが返されることを確認します。
    """
    # テストユーザーの作成
    user, password = test_user
    
    # 削除対象のユーザーを作成
    target_user = await User.create_user(
        username="user_to_delete",
        plain_password="test_password123",
        is_admin=False
    )
    
    # 一般ユーザーのアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # 一般ユーザーが他のユーザーを削除しようとする
    response = await client.delete(
        f"/users/{target_user.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 403, "一般ユーザーによるユーザー削除で403エラーが返されるべきです"
    assert "Not enough permissions" in response.json()["detail"], "エラーメッセージが正しくありません"
    
    # ユーザーが削除されていないことを確認
    not_deleted_user = await User.get_user_by_id(target_user.id)
    assert not_deleted_user is not None, "ユーザーが削除されています"

@pytest.mark.asyncio
async def test_delete_user_unauthorized(client: AsyncClient):
    """
    認証なしでアクセスした場合に401エラーが返されることを確認します。
    """
    # 認証なしでリクエストを送信
    response = await client.delete("/users/1")

    # レスポンスの検証
    assert response.status_code == 401, "認証なしのアクセスで401エラーが返されるべきです"
    assert response.json()["detail"] == "Not authenticated", "エラーメッセージが正しくありません"
