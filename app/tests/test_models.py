import pytest
import pytest_asyncio
import uuid
from sqlalchemy import select

from app.models.user import pwd_context, User


@pytest.fixture
def unique_username():
    """ユニークなユーザー名を生成する"""
    return f"user_{uuid.uuid4()}"

@pytest_asyncio.fixture
async def test_user(unique_username, test_db_session):
    """テスト用のユーザーを作成する"""
    password = "test_password123"
    hashed_password = await User.set_password(password)
    user = User(username=unique_username, hashed_password=hashed_password, is_admin=False)
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    return user, password

@pytest.mark.asyncio
async def test_create_user(unique_username, test_db_session):
    """ユーザーを作成し、フィールドが正しく設定されているかを確認"""
    password = "test_password"
    hashed_password = await User.set_password(password)
    new_user = User(username=unique_username, hashed_password=hashed_password, is_admin=False)
    test_db_session.add(new_user)
    await test_db_session.commit()
    await test_db_session.refresh(new_user)

    assert new_user.id is not None, "ユーザーIDが設定されているか"
    assert new_user.username == unique_username, "ユーザー名が正しいか"
    assert new_user.is_admin == False, "管理者権限が初期値でFalseであるか"
    assert pwd_context.verify(password, new_user.hashed_password), "パスワードが正しくハッシュ化されているか"

@pytest.mark.asyncio
async def test_create_admin_user(unique_username, test_db_session):
    """管理者ユーザーを作成し、is_adminフラグが正しく設定されているかを確認"""
    password = "admin_password123"
    hashed_password = await User.set_password(password)
    admin_user = User(username=unique_username, hashed_password=hashed_password, is_admin=True)
    test_db_session.add(admin_user)
    await test_db_session.commit()
    await test_db_session.refresh(admin_user)
    
    assert admin_user.is_admin == True, "管理者権限が正しく設定されているか"

@pytest.mark.asyncio
async def test_validate_password(test_user, test_db_session):
    """パスワード検証機能が正しく動作するかを確認"""
    user, password = test_user
    
    # 正しいパスワードの検証
    is_valid = await user.valify_password(password)
    assert is_valid == True, "正しいパスワードが検証できているか"
    
    # 間違ったパスワードの検証
    is_valid = await user.valify_password("wrong_password")
    assert is_valid == False, "間違ったパスワードが拒否されているか"

@pytest.mark.asyncio
async def test_set_password():
    """パスワードのハッシュ化が正しく行われるかを確認"""
    password = "new_password123"
    hashed_password = await User.set_password(password)
    
    assert hashed_password != password, "パスワードがハッシュ化されているか"
    assert pwd_context.verify(password, hashed_password), "ハッシュ化されたパスワードが検証できるか"

@pytest.mark.asyncio
async def test_get_user_by_id(test_user, test_db_session):
    """IDによるユーザー取得が正しく動作するかを確認"""
    user, _ = test_user
    
    # ユーザーをIDで取得
    stmt = select(User).where(User.id == user.id)
    result = await test_db_session.execute(stmt)
    retrieved_user = result.scalar_one_or_none()
    
    assert retrieved_user is not None, "ユーザーが取得できているか"
    assert retrieved_user.id == user.id, "正しいユーザーが取得できているか"
    assert retrieved_user.username == user.username, "ユーザー名が一致しているか"

@pytest.mark.asyncio
async def test_get_user_by_username(test_user, test_db_session):
    """ユーザー名によるユーザー取得が正しく動作するかを確認"""
    user, _ = test_user
    
    # ユーザーをユーザー名で取得
    stmt = select(User).where(User.username == user.username)
    result = await test_db_session.execute(stmt)
    retrieved_user = result.scalar_one_or_none()
    
    assert retrieved_user is not None, "ユーザーが取得できているか"
    assert retrieved_user.id == user.id, "正しいユーザーが取得できているか"
    assert retrieved_user.username == user.username, "ユーザー名が一致しているか"

@pytest.mark.asyncio
async def test_get_all_users(test_user, test_db_session):
    """全ユーザー取得が正しく動作するかを確認"""
    user, _ = test_user
    
    # 全ユーザーを取得
    stmt = select(User)
    result = await test_db_session.execute(stmt)
    users = result.scalars().all()
    
    assert len(users) > 0, "ユーザーが取得できているか"
    assert any(u.id == user.id for u in users), "作成したユーザーが含まれているか"

@pytest.mark.asyncio
async def test_update_user(test_user, test_db_session):
    """ユーザー情報の更新が正しく動作するかを確認"""
    user, _ = test_user
    new_username = f"updated_{uuid.uuid4()}"
    
    # ユーザー情報を更新
    stmt = select(User).where(User.id == user.id)
    result = await test_db_session.execute(stmt)
    user_to_update = result.scalar_one_or_none()
    user_to_update.username = new_username
    user_to_update.is_admin = True
    test_db_session.add(user_to_update)
    await test_db_session.commit()
    
    # 更新されたユーザーを取得
    stmt = select(User).where(User.id == user.id)
    result = await test_db_session.execute(stmt)
    updated_user = result.scalar_one_or_none()
    
    assert updated_user.username == new_username, "ユーザー名が更新されているか"
    assert updated_user.is_admin == True, "管理者権限が更新されているか"

@pytest.mark.asyncio
async def test_update_password(test_user, test_db_session):
    """パスワード更新が正しく動作するかを確認"""
    user, old_password = test_user
    new_password = "new_password456"
    
    # パスワードを更新
    stmt = select(User).where(User.id == user.id)
    result = await test_db_session.execute(stmt)
    user_to_update = result.scalar_one_or_none()
    user_to_update.hashed_password = await User.set_password(new_password)
    test_db_session.add(user_to_update)
    await test_db_session.commit()
    
    # 更新されたユーザーを取得
    stmt = select(User).where(User.id == user.id)
    result = await test_db_session.execute(stmt)
    updated_user = result.scalar_one_or_none()
    
    # 古いパスワードが使えなくなっているか確認
    old_password_valid = await updated_user.valify_password(old_password)
    assert old_password_valid == False, "古いパスワードが使えなくなっているか"
    
    # 新しいパスワードが使えるか確認
    new_password_valid = await updated_user.valify_password(new_password)
    assert new_password_valid == True, "新しいパスワードが使えるか"

@pytest.mark.asyncio
async def test_delete_user(test_user, test_db_session):
    """ユーザー削除が正しく動作するかを確認"""
    user, _ = test_user
    
    # ユーザーを削除
    stmt = select(User).where(User.id == user.id)
    result = await test_db_session.execute(stmt)
    user_to_delete = result.scalar_one_or_none()
    await test_db_session.delete(user_to_delete)
    await test_db_session.commit()
    
    # 削除されたユーザーを取得しようとする
    stmt = select(User).where(User.id == user.id)
    result = await test_db_session.execute(stmt)
    deleted_user = result.scalar_one_or_none()
    
    assert deleted_user is None, "ユーザーが削除されているか"
