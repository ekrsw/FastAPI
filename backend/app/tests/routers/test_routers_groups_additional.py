from httpx import AsyncClient
import pytest

from app.models.group import Group
from app.models.user import User
from app.tests.conftest import test_admin, test_user, unique_groupname, client


@pytest.mark.asyncio
async def test_create_group_invalid_name_empty(test_user, client: AsyncClient):
    """
    空のグループ名でグループを作成しようとした場合に
    バリデーションエラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # 空のグループ名でリクエスト
    response = await client.post(
        "/groups/",
        json={"groupname": ""},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 422, "空のグループ名で422エラーが返されるべきです"
    data = response.json()
    assert "groupname must not be empty" in str(data), "エラーメッセージが正しくありません"


@pytest.mark.asyncio
async def test_create_group_invalid_name_too_short(test_user, client: AsyncClient):
    """
    短すぎるグループ名（3文字未満）でグループを作成しようとした場合に
    バリデーションエラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # 短すぎるグループ名でリクエスト
    response = await client.post(
        "/groups/",
        json={"groupname": "ab"},  # 2文字のグループ名
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 422, "短すぎるグループ名で422エラーが返されるべきです"
    data = response.json()
    assert "groupname must be between 3 and 100 characters" in str(data), "エラーメッセージが正しくありません"


@pytest.mark.asyncio
async def test_create_group_invalid_name_too_long(test_user, client: AsyncClient):
    """
    長すぎるグループ名（100文字超過）でグループを作成しようとした場合に
    バリデーションエラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # 長すぎるグループ名でリクエスト
    too_long_name = "a" * 101  # 101文字のグループ名
    response = await client.post(
        "/groups/",
        json={"groupname": too_long_name},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 422, "長すぎるグループ名で422エラーが返されるべきです"
    data = response.json()
    assert "groupname must be between 3 and 100 characters" in str(data), "エラーメッセージが正しくありません"


@pytest.mark.asyncio
async def test_update_group_invalid_name_empty(test_user, unique_groupname, client: AsyncClient):
    """
    空のグループ名でグループを更新しようとした場合に
    バリデーションエラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # テスト用のグループを作成
    group_response = await client.post(
        "/groups/",
        json={"groupname": unique_groupname},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    group_id = group_response.json()["id"]

    # 空のグループ名で更新を試みる
    response = await client.put(
        f"/groups/{group_id}",
        json={"groupname": ""},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 422, "空のグループ名で422エラーが返されるべきです"
    data = response.json()
    assert "groupname must not be empty" in str(data), "エラーメッセージが正しくありません"


@pytest.mark.asyncio
async def test_update_group_invalid_name_too_short(test_user, unique_groupname, client: AsyncClient):
    """
    短すぎるグループ名（3文字未満）でグループを更新しようとした場合に
    バリデーションエラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # テスト用のグループを作成
    group_response = await client.post(
        "/groups/",
        json={"groupname": unique_groupname},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    group_id = group_response.json()["id"]

    # 短すぎるグループ名で更新を試みる
    response = await client.put(
        f"/groups/{group_id}",
        json={"groupname": "ab"},  # 2文字のグループ名
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 422, "短すぎるグループ名で422エラーが返されるべきです"
    data = response.json()
    assert "groupname must be between 3 and 100 characters" in str(data), "エラーメッセージが正しくありません"


@pytest.mark.asyncio
async def test_update_group_invalid_name_too_long(test_user, unique_groupname, client: AsyncClient):
    """
    長すぎるグループ名（100文字超過）でグループを更新しようとした場合に
    バリデーションエラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # テスト用のグループを作成
    group_response = await client.post(
        "/groups/",
        json={"groupname": unique_groupname},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    group_id = group_response.json()["id"]

    # 長すぎるグループ名で更新を試みる
    too_long_name = "a" * 101  # 101文字のグループ名
    response = await client.put(
        f"/groups/{group_id}",
        json={"groupname": too_long_name},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 422, "長すぎるグループ名で422エラーが返されるべきです"
    data = response.json()
    assert "groupname must be between 3 and 100 characters" in str(data), "エラーメッセージが正しくありません"


@pytest.mark.asyncio
async def test_update_group_unauthorized(test_user, unique_groupname, client: AsyncClient):
    """
    認証なしでグループを更新しようとした場合に401エラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # テスト用のグループを作成
    group_response = await client.post(
        "/groups/",
        json={"groupname": unique_groupname},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    group_id = group_response.json()["id"]

    # 認証なしでグループ更新を試みる
    new_groupname = f"updated_{unique_groupname}"
    response = await client.put(
        f"/groups/{group_id}",
        json={"groupname": new_groupname}
    )

    # レスポンスの検証
    assert response.status_code == 401, "認証なしのアクセスで401エラーが返されるべきです"
    assert response.json()["detail"] == "Not authenticated", "エラーメッセージが正しくありません"


@pytest.mark.asyncio
async def test_delete_group_unauthorized(test_admin, unique_groupname, client: AsyncClient):
    """
    認証なしでグループを削除しようとした場合に401エラーが返されることを確認します。
    """
    # 管理者ユーザーの作成とアクセストークンの取得
    admin, admin_password = test_admin
    
    token_response = await client.post(
        "/auth/token",
        data={"username": admin.username, "password": admin_password}
    )
    access_token = token_response.json()["access_token"]

    # テスト用のグループを作成
    group_response = await client.post(
        "/groups/",
        json={"groupname": unique_groupname},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    group_id = group_response.json()["id"]

    # 認証なしでグループ削除を試みる
    response = await client.delete(f"/groups/{group_id}")

    # レスポンスの検証
    assert response.status_code == 401, "認証なしのアクセスで401エラーが返されるべきです"
    assert response.json()["detail"] == "Not authenticated", "エラーメッセージが正しくありません"


@pytest.mark.asyncio
async def test_read_all_groups_unauthorized(client: AsyncClient):
    """
    認証なしでグループ一覧を取得しようとした場合に401エラーが返されることを確認します。
    """
    # 認証なしでリクエストを送信
    response = await client.get("/groups/")

    # レスポンスの検証
    assert response.status_code == 401, "認証なしのアクセスで401エラーが返されるべきです"
    assert response.json()["detail"] == "Not authenticated", "エラーメッセージが正しくありません"


@pytest.mark.asyncio
async def test_create_group_invalid_json(test_user, client: AsyncClient):
    """
    不正なJSONリクエストボディでグループを作成しようとした場合に
    エラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # 不正なJSONリクエストボディ（必須フィールドの欠落）
    response = await client.post(
        "/groups/",
        json={},  # groupnameフィールドが欠落
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 422, "不正なJSONリクエストボディで422エラーが返されるべきです"


@pytest.mark.asyncio
async def test_update_group_invalid_json(test_user, unique_groupname, client: AsyncClient):
    """
    不正なJSONリクエストボディでグループを更新しようとした場合に
    エラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # テスト用のグループを作成
    group_response = await client.post(
        "/groups/",
        json={"groupname": unique_groupname},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    group_id = group_response.json()["id"]

    # 不正なJSONリクエストボディ（必須フィールドの欠落）
    response = await client.put(
        f"/groups/{group_id}",
        json={},  # groupnameフィールドが欠落
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 422, "不正なJSONリクエストボディで422エラーが返されるべきです"


@pytest.mark.asyncio
async def test_access_with_invalid_token(test_user, client: AsyncClient):
    """
    不正なトークンでアクセスした場合に401エラーが返されることを確認します。
    """
    # 不正なトークンでリクエストを送信
    invalid_token = "invalid_token_string"
    response = await client.get(
        "/groups/",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 401, "不正なトークンで401エラーが返されるべきです"
    assert "Could not validate credentials" in response.json()["detail"], "エラーメッセージが正しくありません"


@pytest.mark.asyncio
async def test_access_with_malformed_token(test_user, client: AsyncClient):
    """
    不正な形式のトークンでアクセスした場合に401エラーが返されることを確認します。
    """
    # 不正な形式のトークンでリクエストを送信
    response = await client.get(
        "/groups/",
        headers={"Authorization": "InvalidFormat Token"}
    )

    # レスポンスの検証
    assert response.status_code == 401, "不正な形式のトークンで401エラーが返されるべきです"
    assert "Not authenticated" in response.json()["detail"], "エラーメッセージが正しくありません"
