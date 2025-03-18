from httpx import AsyncClient
import pytest

from app.models.group import Group
from app.models.user import User
from app.tests.conftest import test_admin, test_user, unique_groupname, client


@pytest.mark.asyncio
async def test_create_group_success(test_user, unique_groupname, client: AsyncClient):
    """
    認証済みユーザーが新しいグループを作成できることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # /groups/ エンドポイントにPOSTリクエストを送信
    response = await client.post(
        "/groups/",
        json={"groupname": unique_groupname},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 200, f"グループの作成に失敗しました: {response.text}"
    data = response.json()
    assert data["groupname"] == unique_groupname, "作成したグループ名が正しくありません"
    assert "id" in data, "グループIDが返されていません"

@pytest.mark.asyncio
async def test_create_group_unauthorized(client: AsyncClient, unique_groupname):
    """
    認証なしでグループを作成しようとした場合に401エラーが返されることを確認します。
    """
    # 認証なしでリクエストを送信
    response = await client.post(
        "/groups/",
        json={"groupname": unique_groupname}
    )

    # レスポンスの検証
    assert response.status_code == 401, "認証なしのアクセスで401エラーが返されるべきです"
    assert response.json()["detail"] == "Not authenticated", "エラーメッセージが正しくありません"

@pytest.mark.asyncio
async def test_read_group_by_id_success(test_user, unique_groupname, client: AsyncClient):
    """
    正しい認証情報と存在するグループIDで、グループ情報を取得できることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
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

    # /groups/{group_id} エンドポイントにリクエストを送信
    response = await client.get(
        f"/groups/{group_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 200, f"グループ情報の取得に失敗しました: {response.text}"
    data = response.json()
    assert data["id"] == group_id, "取得したグループIDが正しくありません"
    assert data["groupname"] == unique_groupname, "取得したグループ名が正しくありません"

@pytest.mark.asyncio
async def test_read_group_by_id_not_found(test_user, client: AsyncClient):
    """
    存在しないグループIDを指定した場合に404エラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # 存在しないグループIDでリクエストを送信
    non_existent_id = 99999
    response = await client.get(
        f"/groups/{non_existent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 404, "存在しないグループIDで404エラーが返されるべきです"
    assert response.json()["detail"] == "Group not found", "エラーメッセージが正しくありません"

@pytest.mark.asyncio
async def test_read_group_by_id_unauthorized(client: AsyncClient):
    """
    認証なしでアクセスした場合に401エラーが返されることを確認します。
    """
    # 認証なしでリクエストを送信
    response = await client.get("/groups/1")

    # レスポンスの検証
    assert response.status_code == 401, "認証なしのアクセスで401エラーが返されるべきです"
    assert response.json()["detail"] == "Not authenticated", "エラーメッセージが正しくありません"

@pytest.mark.asyncio
async def test_read_all_groups_success(test_user, unique_groupname, client: AsyncClient):
    """
    認証済みユーザーが全てのグループ情報を取得できることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # テスト用のグループを作成
    group1_name = f"{unique_groupname}_1"
    group2_name = f"{unique_groupname}_2"
    
    group1_response = await client.post(
        "/groups/",
        json={"groupname": group1_name},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    group1_id = group1_response.json()["id"]
    
    group2_response = await client.post(
        "/groups/",
        json={"groupname": group2_name},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    group2_id = group2_response.json()["id"]

    # /groups エンドポイントにリクエストを送信
    response = await client.get(
        "/groups/",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 200, f"グループ情報の取得に失敗しました: {response.text}"
    data = response.json()
    
    # レスポンスが配列であることを確認
    assert isinstance(data, list), "レスポンスは配列であるべきです"
    
    # 少なくとも2つのグループが存在することを確認
    assert len(data) >= 2, "取得したグループ数が正しくありません"
    
    # 作成したグループの情報が含まれていることを確認
    group_ids = [g["id"] for g in data]
    assert group1_id in group_ids, "作成したグループ1の情報が含まれていません"
    assert group2_id in group_ids, "作成したグループ2の情報が含まれていません"

@pytest.mark.asyncio
async def test_read_all_groups_empty(test_user, client: AsyncClient):
    """
    グループが存在しない状態でグループ一覧を取得できることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]
    
    # 全てのグループを削除
    groups = await Group.get_all_groups()
    for group in groups:
        await Group.delete_group_permanently(group_id=group.id)

    # /groups エンドポイントにリクエストを送信
    response = await client.get(
        "/groups/",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 200, "認証済みユーザーは空のリストを取得できるべきです"
    data = response.json()
    assert isinstance(data, list), "レスポンスは配列であるべきです"
    assert len(data) == 0, "グループが存在しない場合は空のリストが返されるべきです"

@pytest.mark.asyncio
async def test_update_group_success(test_user, unique_groupname, client: AsyncClient):
    """
    認証済みユーザーがグループ情報を更新できることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
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

    # 新しいグループ名
    new_groupname = f"updated_{unique_groupname}"
    
    # /groups/{group_id} エンドポイントにPUTリクエストを送信
    response = await client.put(
        f"/groups/{group_id}",
        json={"groupname": new_groupname},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 200, f"グループ情報の更新に失敗しました: {response.text}"
    data = response.json()
    assert data["id"] == group_id, "更新したグループIDが正しくありません"
    assert data["groupname"] == new_groupname, "グループ名が更新されていません"

@pytest.mark.asyncio
async def test_update_group_not_found(test_user, unique_groupname, client: AsyncClient):
    """
    存在しないグループIDを指定した場合に404エラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": user.username, "password": password}
    )
    access_token = token_response.json()["access_token"]

    # 存在しないグループIDでリクエストを送信
    non_existent_id = 99999
    response = await client.put(
        f"/groups/{non_existent_id}",
        json={"groupname": unique_groupname},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 404, "存在しないグループIDで404エラーが返されるべきです"
    assert response.json()["detail"] == "Group not found", "エラーメッセージが正しくありません"

@pytest.mark.asyncio
async def test_delete_group_by_admin_success(test_admin, unique_groupname, client: AsyncClient):
    """
    管理者がグループを削除できることを確認します。
    """
    # 管理者ユーザーの作成とアクセストークンの取得
    admin, admin_password = test_admin
    
    # 管理者のアクセストークンを取得
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

    # 管理者がグループを削除
    response = await client.delete(
        f"/groups/{group_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 200, f"グループの削除に失敗しました: {response.text}"
    data = response.json()
    assert data["message"] == "Group deleted successfully", "削除成功メッセージが正しくありません"
    
    # 削除されたグループが存在しないことを確認
    deleted_group = await Group.get_group_by_id(group_id=group_id)
    assert deleted_group is None, "グループが物理削除されていません"

@pytest.mark.asyncio
async def test_delete_group_not_found(test_admin, client: AsyncClient):
    """
    存在しないグループIDを指定した場合に404エラーが返されることを確認します。
    """
    # 管理者ユーザーの作成とアクセストークンの取得
    admin, admin_password = test_admin
    
    # 管理者のアクセストークンを取得
    token_response = await client.post(
        "/auth/token",
        data={"username": admin.username, "password": admin_password}
    )
    access_token = token_response.json()["access_token"]

    # 存在しないグループIDでリクエストを送信
    non_existent_id = 99999
    response = await client.delete(
        f"/groups/{non_existent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 404, "存在しないグループIDで404エラーが返されるべきです"
    assert response.json()["detail"] == "Group not found", "エラーメッセージが正しくありません"

@pytest.mark.asyncio
async def test_delete_group_forbidden(test_user, unique_groupname, client: AsyncClient):
    """
    一般ユーザーがグループを削除しようとした場合に403エラーが返されることを確認します。
    """
    # テストユーザーの作成とアクセストークンの取得
    user, password = test_user
    
    # /auth/token エンドポイントでアクセストークンを取得
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

    # 一般ユーザーがグループを削除しようとする
    response = await client.delete(
        f"/groups/{group_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # レスポンスの検証
    assert response.status_code == 403, "一般ユーザーによるグループ削除で403エラーが返されるべきです"
    assert "Not enough permissions" in response.json()["detail"], "エラーメッセージが正しくありません"
    
    # グループが削除されていないことを確認
    not_deleted_group = await Group.get_group_by_id(group_id=group_id)
    assert not_deleted_group is not None, "グループが削除されています"


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
