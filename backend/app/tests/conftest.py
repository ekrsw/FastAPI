from httpx import AsyncClient, ASGITransport
import pytest
import pytest_asyncio
import uuid

from app.db.database import Base, Database
from app.main import app
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

@pytest.fixture
def app_test():
    return app

@pytest_asyncio.fixture
async def client(app_test):
    async with AsyncClient(
        transport=ASGITransport(app=app_test),
        base_url="http://test"
    ) as client:
        yield client

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """テスト用のデータベースをセットアップする"""
    database = Database()
    engine = database.engine
    # テスト前にテーブルを作成
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # テスト後にテーブルを削除
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)