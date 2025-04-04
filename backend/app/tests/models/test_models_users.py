import pytest
import pytest_asyncio
from sqlalchemy import select
import uuid

from app.models.user import pwd_context, User
from app.tests.conftest import test_admin, test_user, unique_username


@pytest.mark.asyncio
async def test_create_user(unique_username):
    """ユーザーを作成し、フィールドが正しく設定されているかを確認"""
    password = "test_password"
    new_user = await User.create_user(obj_in={
        "username": unique_username,
        "password": password,
        "is_admin": False
    })

    assert new_user.id is not None, "ユーザーIDが設定されているか"
    assert new_user.username == unique_username, "ユーザー名が正しいか"
    assert new_user.is_admin == False, "管理者権限が初期値でFalseであるか"
    assert pwd_context.verify(password, new_user.hashed_password), "パスワードが正しくハッシュ化されているか"

    exist_user = await User.get_user_by_username(unique_username)
    assert exist_user is not None, "ユーザーがデータベースに保存されているか"

@pytest.mark.asyncio
async def test_create_admin_user(unique_username):
    """管理者ユーザーを作成し、is_adminフラグが正しく設定されているかを確認"""
    password = "admin_password123"
    admin_user = await User.create_user(obj_in={
        "username": unique_username,
        "password": password,
        "is_admin": True
    })
    
    exist_user = await User.get_user_by_username(unique_username)
    assert admin_user.is_admin == True, "管理者権限が正しく設定されているか"
    assert exist_user is not None, "ユーザーがデータベースに保存されているか"
    assert exist_user.is_admin == True, "保存されたユーザーに管理者権限が正しく設定されているか"

@pytest.mark.asyncio
async def test_validate_password(test_user):
    """パスワード検証機能が正しく動作するかを確認"""
    user, password = test_user

    # 正しいパスワードの検証
    is_valid = await user.verify_password(password)
    assert is_valid == True, "正しいパスワードが検証できているか"
    
    # 間違ったパスワードの検証
    is_valid = await user.verify_password("wrong_password")
    assert is_valid == False, "間違ったパスワードが拒否されているか"

@pytest.mark.asyncio
async def test_set_password():
    """パスワードのハッシュ化が正しく行われるかを確認"""
    password = "new_password123"
    hashed_password = await User.set_password(password)
    
    assert hashed_password != password, "パスワードがハッシュ化されているか"
    assert pwd_context.verify(password, hashed_password), "ハッシュ化されたパスワードが検証できるか"

@pytest.mark.asyncio
async def test_get_user_by_id(test_user):
    """IDによるユーザー取得が正しく動作するかを確認（include_deleteの動作確認を含む）"""
    user, _ = test_user
    
    # 通常のユーザー取得（デフォルト: include_delete=False）
    retrieved_user = await User.get_user_by_id(user.id)
    assert retrieved_user is not None, "ユーザーが取得できているか"
    assert retrieved_user.id == user.id, "正しいユーザーが取得できているか"
    assert retrieved_user.username == user.username, "ユーザー名が一致しているか"

    # ユーザーを論理削除
    await User.delete_user(user.id)

    # 論理削除後、include_delete=Falseで取得を試みる
    retrieved_user = await User.get_user_by_id(user.id, include_deleted=False)
    assert retrieved_user is None, "論理削除されたユーザーが通常の取得で取得できないか"

    # 論理削除後、include_delete=Trueで取得
    retrieved_user = await User.get_user_by_id(user.id, include_deleted=True)
    assert retrieved_user is not None, "論理削除されたユーザーが取得できているか"
    assert retrieved_user.id == user.id, "正しいユーザーが取得できているか"
    assert retrieved_user.deleted_at is not None, "deleted_atが設定されているか"

@pytest.mark.asyncio
async def test_get_user_by_username(test_user):
    """ユーザー名によるユーザー取得が正しく動作するかを確認"""
    user, _ = test_user
    
    # ユーザーをユーザー名で取得
    retrieved_user = await User.get_user_by_username(user.username)
    
    assert retrieved_user is not None, "ユーザーが取得できているか"
    assert retrieved_user.id == user.id, "正しいユーザーが取得できているか"
    assert retrieved_user.username == user.username, "ユーザー名が一致しているか"

@pytest.mark.asyncio
async def test_get_all_users(test_user):
    """全ユーザー取得が正しく動作するかを確認"""
    user, _ = test_user
    
    # 全ユーザーを取得
    users = await User.get_all_users()
    
    assert len(users) > 0, "ユーザーが取得できているか"
    assert any(u.id == user.id for u in users), "作成したユーザーが含まれているか"

@pytest.mark.asyncio
async def test_update_user(test_user):
    """ユーザー情報の更新が正しく動作するかを確認"""
    user, _ = test_user
    new_username = f"updated_{uuid.uuid4()}"
    
    # ユーザー情報を更新
    updated_user = await User.update_user(
        db_obj=user,
        obj_in={
            "username": new_username,
            "is_admin": True
        }
    )
    
    assert updated_user.username == new_username, "ユーザー名が更新されているか"
    assert updated_user.is_admin == True, "管理者権限が更新されているか"

@pytest.mark.asyncio
async def test_update_password(test_user):
    """パスワード更新が正しく動作するかを確認"""
    user, old_password = test_user
    new_password = "new_password456"
    
    # パスワードを更新
    updated_user = await User.update_user(
        db_obj=user,
        obj_in={"password": new_password}
    )
    
    # 古いパスワードが使えなくなっているか確認
    old_password_valid = await updated_user.verify_password(old_password)
    assert old_password_valid == False, "古いパスワードが使えなくなっているか"
    
    # 新しいパスワードが使えるか確認
    new_password_valid = await updated_user.verify_password(new_password)
    assert new_password_valid == True, "新しいパスワードが使えるか"

@pytest.mark.asyncio
async def test_delete_user(test_user):
    """論理削除が正しく動作するかを確認"""
    user, _ = test_user
    
    # ユーザーを論理削除
    await User.delete_user(user.id)
    
    # 削除されたユーザーを取得（論理削除されたレコードも含める）
    deleted_user = await User.get_user_by_id(user.id, include_deleted=True)
    
    assert deleted_user is not None, "ユーザーが存在しているか（論理削除を含む）"
    assert deleted_user.deleted_at is not None, "deleted_atが設定されているか"

@pytest.mark.asyncio
async def test_get_user_by_username_with_deleted(test_user):
    """ユーザー名による取得でinclude_deletedの動作を確認"""
    user, _ = test_user
    
    # ユーザーを論理削除
    await User.delete_user(user.id)
    
    # 論理削除後、include_deleted=Falseで取得を試みる
    retrieved_user = await User.get_user_by_username(user.username, include_deleted=False)
    assert retrieved_user is None, "論理削除されたユーザーが通常の取得で取得できないか"
    
    # 論理削除後、include_deleted=Trueで取得
    retrieved_user = await User.get_user_by_username(user.username, include_deleted=True)
    assert retrieved_user is not None, "論理削除されたユーザーが取得できているか"
    assert retrieved_user.username == user.username, "ユーザー名が一致しているか"
    assert retrieved_user.deleted_at is not None, "deleted_atが設定されているか"

@pytest.mark.asyncio
async def test_get_all_users_with_deleted(test_user):
    """全ユーザー取得でinclude_deletedの動作を確認"""
    user, _ = test_user
    
    # 追加のユーザーを作成
    additional_user = await User.create_user(obj_in={
        "username": f"additional_{uuid.uuid4()}",
        "password": "password123",
        "is_admin": False
    })
    
    # 一人のユーザーを論理削除
    await User.delete_user(user.id)
    
    # include_deleted=Falseで全ユーザー取得
    active_users = await User.get_all_users(include_deleted=False)
    assert len(active_users) == 1, "アクティブなユーザーのみが取得されているか"
    assert all(u.deleted_at is None for u in active_users), "全てのユーザーが未削除か"
    
    # include_deleted=Trueで全ユーザー取得
    all_users = await User.get_all_users(include_deleted=True)
    assert len(all_users) == 2, "削除済みユーザーを含めて全て取得されているか"
    assert any(u.deleted_at is not None for u in all_users), "削除済みユーザーが含まれているか"

@pytest.mark.asyncio
async def test_update_user_edge_cases(test_user):
    """ユーザー更新の特殊ケースを確認"""
    user, _ = test_user
    
    # ユーザーを論理削除
    await User.delete_user(user.id)
    
    # 論理削除されたユーザーの更新を試みる
    with pytest.raises(Exception):
        await User.update_user(
            db_obj=user,
            obj_in={"username": "new_name"}
        )
    
    # 存在しないユーザーの更新を試みる
    non_existent_user = User(id=uuid.uuid4(), username="non_existent")
    with pytest.raises(Exception):
        await User.update_user(
            db_obj=non_existent_user,
            obj_in={"username": "new_name"}
        )
    
    # 一部のフィールドのみを更新
    active_user = await User.create_user(obj_in={
        "username": f"partial_{uuid.uuid4()}",
        "password": "password123",
        "is_admin": False
    })
    updated_user = await User.update_user(
        db_obj=active_user,
        obj_in={"is_admin": True}
    )
    assert updated_user.is_admin == True, "is_adminが更新されているか"
    assert updated_user.username == active_user.username, "更新していないフィールドが保持されているか"

@pytest.mark.asyncio
async def test_delete_user_edge_cases(test_user):
    """ユーザー削除の特殊ケースを確認"""
    user, _ = test_user
    
    # ユーザーを論理削除
    await User.delete_user(user.id)
    
    # 既に論理削除されているユーザーを再度論理削除
    await User.delete_user(user.id)
    deleted_user = await User.get_user_by_id(user.id, include_deleted=True)
    assert deleted_user is not None, "ユーザーが存在しているか"
    
    # 存在しないユーザーIDで論理削除を試みる
    non_existent_id = uuid.uuid4()
    with pytest.raises(Exception):
        await User.delete_user(non_existent_id)

@pytest.mark.asyncio
async def test_delete_user_permanently_edge_cases(test_user):
    """物理削除の特殊ケースを確認"""
    user, _ = test_user
    
    # 論理削除せずに直接物理削除
    await User.delete_user_permanently(user.id)
    deleted_user = await User.get_user_by_id(user.id, include_deleted=True)
    assert deleted_user is None, "ユーザーが完全に削除されているか"
    
    # 存在しないユーザーIDで物理削除を試みる
    non_existent_id = uuid.uuid4()
    with pytest.raises(Exception):
        await User.delete_user_permanently(non_existent_id)

@pytest.mark.asyncio
async def test_delete_user_permanently(test_user):
    """物理削除が正しく動作するかを確認"""
    user, _ = test_user
    
    # ユーザーを物理削除
    await User.delete_user_permanently(user.id)
    
    # 削除されたユーザーを取得しようとする
    deleted_user = await User.get_user_by_id(user.id)
    
    assert deleted_user is None, "ユーザーが完全に削除されているか"
