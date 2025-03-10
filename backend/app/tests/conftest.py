import pytest
import pytest_asyncio
import uuid

from app.models.user import User


@pytest.fixture
def unique_username():
    """ユニークなユーザー名を生成する"""
    return f"user_{uuid.uuid4()}"

@pytest_asyncio.fixture
async def test_user(unique_username):
    """テスト用の一般ユーザーを作成する"""
    password = "test_password123"
    user = await User.create_user(
        username=unique_username,
        plain_password=password,
        is_admin=False)
    return user, password

@pytest_asyncio.fixture
async def test_admin(unique_username):
    """テスト用の管理者ユーザーを作成する"""
    password = "test_admin_password123"
    # テスト用の管理者ユーザーを作成
    admin_user = await User.create_user(
        username=unique_username,
        plain_password=password,
        is_admin=True
    )
    return admin_user, password