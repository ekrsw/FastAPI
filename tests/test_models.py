import pytest
import uuid
import asyncio

from app.models.user import pwd_context, User


@pytest.fixture
def unique_username():
    """ユニークなユーザー名を生成する"""
    return f"user_{uuid.uuid4()}"

@pytest.mark.asyncio
async def test_create_user(unique_username):
    """ユーザーを作成し、フィールドが正しく設定されているかを確認"""
    password = "test_password"
    new_user = await User.create_user(username=unique_username, plain_password=password)

    assert new_user.id is not None, "ユーザーIDが設定されているか"
    assert new_user.username == unique_username, "ユーザー名が正しいか"
    assert new_user.is_admin == False, "管理者権限が初期値でFalseであるか"
    assert pwd_context.verify(password, new_user.hashed_password), "パスワードが正しくハッシュ化されているか"
