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
    new_user = await User.create_user(username=unique_username, plain_password=password)

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
    admin_user = await User.create_user(username=unique_username, plain_password=password, is_admin=True)
    
    exist_user = await User.get_user_by_username(unique_username)
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
    """IDによるユーザー取得が正しく動作するかを確認"""
    user, _ = test_user
    
    # ユーザーをIDで取得
    retrieved_user = await User.get_user_by_id(user.id)
    
    assert retrieved_user is not None, "ユーザーが取得できているか"
    assert retrieved_user.id == user.id, "正しいユーザーが取得できているか"
    assert retrieved_user.username == user.username, "ユーザー名が一致しているか"

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
    await User.update_user(user.id, new_username, is_admin=True)
    
    # 更新されたユーザーを取得
    updated_user = await User.get_user_by_id(user.id)
    
    assert updated_user.username == new_username, "ユーザー名が更新されているか"
    assert updated_user.is_admin == True, "管理者権限が更新されているか"

@pytest.mark.asyncio
async def test_update_password(test_user):
    """パスワード更新が正しく動作するかを確認"""
    user, old_password = test_user
    new_password = "new_password456"
    
    # パスワードを更新
    await User.update_password(user.id, new_password)
    
    # 更新されたユーザーを取得
    updated_user = await User.get_user_by_id(user.id)
    
    # 古いパスワードが使えなくなっているか確認
    old_password_valid = await updated_user.verify_password(old_password)
    assert old_password_valid == False, "古いパスワードが使えなくなっているか"
    
    # 新しいパスワードが使えるか確認
    new_password_valid = await updated_user.verify_password(new_password)
    assert new_password_valid == True, "新しいパスワードが使えるか"

@pytest.mark.asyncio
async def test_delete_user(test_user):
    """ユーザー削除が正しく動作するかを確認"""
    user, _ = test_user
    
    # ユーザーを削除
    await User.delete_user(user.id)
    
    # 削除されたユーザーを取得しようとする
    deleted_user = await User.get_user_by_id(user.id)
    
    assert deleted_user is None, "ユーザーが削除されているか"
