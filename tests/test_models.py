import pytest
import uuid
import asyncio

from app.models.user import User


@pytest.fixture
def unique_username():
    """ユニークなユーザー名を生成する"""
    return f"user_{uuid.uuid4()}"

async def test_create_user(unique_username):
    """ユーザーを作成し、フィールドが正しく設定されているかを確認"""
    password = "test_password"
    