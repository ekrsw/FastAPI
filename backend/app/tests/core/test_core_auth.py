from datetime import datetime, timedelta, timezone
import pytest
from jose import jwt, JWTError
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException, status

from app.core.auth import (
    create_jwt_token,
    create_access_token,
    decode_token,
    authenticate_user,
    get_current_user
)
from app.models.user import User


def test_create_jwt_token_with_default_expiration():
    """デフォルトの有効期限（15分）でJWTトークンが正しく生成されることをテストします。"""
    # テストデータの準備
    test_data = {"sub": "testuser"}
    secret_key = "test_secret"
    algorithm = "HS256"

    # トークンの生成
    token = create_jwt_token(
        data=test_data,
        secret_key=secret_key,
        algorithm=algorithm
    )

    # トークンのデコードと検証
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    
    # ペイロードの検証
    assert payload["sub"] == "testuser"
    
    # 有効期限の検証（デフォルト15分）
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    current_time = datetime.now(timezone.utc)
    time_diff = exp_time - current_time
    
    # 14分から15分の間であることを確認（1分の余裕を持たせる）
    assert timedelta(minutes=14) <= time_diff <= timedelta(minutes=15)


def test_create_jwt_token_with_custom_expiration():
    """カスタムの有効期限でJWTトークンが正しく生成されることをテストします。"""
    # テストデータの準備
    test_data = {"sub": "testuser"}
    secret_key = "test_secret"
    algorithm = "HS256"
    expires_delta = timedelta(hours=1)

    # トークンの生成
    token = create_jwt_token(
        data=test_data,
        secret_key=secret_key,
        algorithm=algorithm,
        expires_delta=expires_delta
    )

    # トークンのデコードと検証
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    
    # ペイロードの検証
    assert payload["sub"] == "testuser"
    
    # 有効期限の検証（1時間）
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    current_time = datetime.now(timezone.utc)
    time_diff = exp_time - current_time
    
    # 59分から60分の間であることを確認（1分の余裕を持たせる）
    assert timedelta(minutes=59) <= time_diff <= timedelta(minutes=60)


def test_create_jwt_token_payload_content():
    """JWTトークンのペイロードが正しい内容を含んでいることをテストします。"""
    # テストデータの準備
    test_data = {
        "sub": "testuser",
        "email": "test@example.com",
        "role": "admin"
    }
    secret_key = "test_secret"
    algorithm = "HS256"

    # トークンの生成
    token = create_jwt_token(
        data=test_data,
        secret_key=secret_key,
        algorithm=algorithm
    )

    # トークンのデコードと検証
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    
    # すべてのペイロードフィールドの検証
    assert payload["sub"] == "testuser"
    assert payload["email"] == "test@example.com"
    assert payload["role"] == "admin"
    assert "exp" in payload  # 有効期限フィールドが存在することを確認


def test_create_access_token_with_default_expiration():
    """デフォルトの有効期限でアクセストークンが正しく生成されることをテストします。"""
    from app.core.config import settings
    
    # テストデータの準備
    test_data = {"sub": "testuser"}
    
    # トークンの生成
    token = create_access_token(data=test_data)
    
    # トークンのデコードと検証
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )
    
    # ペイロードの検証
    assert payload["sub"] == "testuser"
    
    # 有効期限の検証（設定ファイルのデフォルト値）
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    current_time = datetime.now(timezone.utc)
    time_diff = exp_time - current_time
    
    # 設定された時間の前後1分以内であることを確認
    expected_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    assert expected_delta - timedelta(minutes=1) <= time_diff <= expected_delta


def test_create_access_token_with_custom_expiration():
    """カスタムの有効期限でアクセストークンが正しく生成されることをテストします。"""
    from app.core.config import settings
    
    # テストデータの準備
    test_data = {"sub": "testuser"}
    custom_expires_delta = timedelta(hours=2)
    
    # トークンの生成
    token = create_access_token(
        data=test_data,
        expires_delta=custom_expires_delta
    )
    
    # トークンのデコードと検証
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )
    
    # ペイロードの検証
    assert payload["sub"] == "testuser"
    
    # 有効期限の検証（2時間）
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    current_time = datetime.now(timezone.utc)
    time_diff = exp_time - current_time
    
    # 設定された時間の前後1分以内であることを確認
    assert timedelta(hours=2) - timedelta(minutes=1) <= time_diff <= timedelta(hours=2)


def test_create_access_token_with_additional_claims():
    """追加のクレームを含むアクセストークンが正しく生成されることをテストします。"""
    from app.core.config import settings
    
    # テストデータの準備（追加のクレームを含む）
    test_data = {
        "sub": "testuser",
        "role": "admin",
        "permissions": ["read", "write"]
    }
    
    # トークンの生成
    token = create_access_token(data=test_data)
    
    # トークンのデコードと検証
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )
    
    # すべてのクレームの検証
    assert payload["sub"] == "testuser"
    assert payload["role"] == "admin"
    assert payload["permissions"] == ["read", "write"]
    assert "exp" in payload


def test_decode_token_success():
    """有効なトークンが正しくデコードされることをテストします。"""
    # テストデータの準備
    test_data = {
        "sub": "testuser",
        "role": "admin",
        "exp": datetime.now(timezone.utc).timestamp() + 3600  # 1時間後
    }
    secret_key = "test_secret"
    algorithm = "HS256"
    
    # トークンの生成
    token = jwt.encode(test_data, secret_key, algorithm=algorithm)
    
    # トークンのデコード
    payload = decode_token(token, secret_key, [algorithm])
    
    # ペイロードの検証
    assert payload["sub"] == "testuser"
    assert payload["role"] == "admin"
    assert "exp" in payload


def test_decode_token_with_multiple_algorithms():
    """複数のアルゴリズムを指定してトークンをデコードできることをテストします。"""
    # テストデータの準備
    test_data = {"sub": "testuser"}
    secret_key = "test_secret"
    algorithm = "HS256"
    
    # トークンの生成
    token = jwt.encode(test_data, secret_key, algorithm=algorithm)
    
    # 複数のアルゴリズムを指定してデコード
    payload = decode_token(token, secret_key, ["HS384", "HS256", "HS512"])
    
    # ペイロードの検証
    assert payload["sub"] == "testuser"


def test_decode_token_with_invalid_token():
    """無効なトークンを処理した際に適切な例外が発生することをテストします。"""
    secret_key = "test_secret"
    invalid_token = "invalid.token.string"
    
    # 無効なトークンのデコードで例外が発生することを確認
    with pytest.raises(JWTError):
        decode_token(invalid_token, secret_key, ["HS256"])


def test_decode_token_with_expired_token():
    """期限切れトークンを処理した際に適切な例外が発生することをテストします。"""
    # 期限切れのテストデータを準備
    test_data = {
        "sub": "testuser",
        "exp": datetime.now(timezone.utc).timestamp() - 3600  # 1時間前
    }
    secret_key = "test_secret"
    algorithm = "HS256"
    
    # 期限切れトークンの生成
    expired_token = jwt.encode(test_data, secret_key, algorithm=algorithm)
    
    # 期限切れトークンのデコードで例外が発生することを確認
    with pytest.raises(JWTError):
        decode_token(expired_token, secret_key, [algorithm])


@pytest.mark.asyncio
async def test_authenticate_user_success():
    """正しい認証情報でユーザー認証が成功することをテストします。"""
    # モックユーザーの準備
    mock_user = AsyncMock(spec=User)
    mock_user.verify_password = AsyncMock()
    mock_user.verify_password.return_value = True
    
    # get_user_by_usernameをモック化
    with patch.object(
        User, 'get_user_by_username', new_callable=AsyncMock
    ) as mock_get_user:
        mock_get_user.return_value = mock_user
        
        # 認証実行
        user = await authenticate_user("testuser", "correct_password")
        
        # 結果の検証
        assert user is not None
        mock_get_user.assert_called_once_with("testuser")
        mock_user.verify_password.assert_awaited_once_with("correct_password")


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password():
    """誤ったパスワードで認証が失敗することをテストします。"""
    # モックユーザーの準備
    mock_user = AsyncMock(spec=User)
    mock_user.verify_password = AsyncMock()
    mock_user.verify_password.return_value = False
    
    # get_user_by_usernameをモック化
    with patch.object(
        User, 'get_user_by_username', new_callable=AsyncMock
    ) as mock_get_user:
        mock_get_user.return_value = mock_user
        
        # 誤ったパスワードで認証実行
        user = await authenticate_user("testuser", "wrong_password")
        
        # 結果の検証
        assert user is None
        mock_get_user.assert_called_once_with("testuser")
        mock_user.verify_password.assert_awaited_once_with("wrong_password")


@pytest.mark.asyncio
async def test_authenticate_user_nonexistent_user():
    """存在しないユーザーで認証が失敗することをテストします。"""
    # get_user_by_usernameをモック化して存在しないユーザーをシミュレート
    with patch.object(
        User, 'get_user_by_username', new_callable=AsyncMock
    ) as mock_get_user:
        mock_get_user.return_value = None
        
        # 存在しないユーザーで認証実行
        user = await authenticate_user("nonexistent_user", "any_password")
        
        # 結果の検証
        assert user is None
        mock_get_user.assert_called_once_with("nonexistent_user")


@pytest.mark.asyncio
async def test_get_current_user_success():
    """有効なトークンで現在のユーザーが正しく取得できることをテストします。"""
    from app.core.config import settings
    
    # テストユーザーの準備
    mock_user = AsyncMock(spec=User)
    mock_user.username = "testuser"
    
    # get_user_by_usernameをモック化
    with patch.object(
        User, 'get_user_by_username', new_callable=AsyncMock
    ) as mock_get_user:
        mock_get_user.return_value = mock_user
        
        # 有効なトークンの生成
        token = create_access_token({"sub": "testuser"})
        
        # ユーザー取得の実行
        user = await get_current_user(token)
        
        # 結果の検証
        assert user is not None
        assert user == mock_user
        mock_get_user.assert_called_once_with(username="testuser")


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """無効なトークンで認証が失敗することをテストします。"""
    # 無効なトークンでテスト
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid.token.string")
    
    # エラーの検証
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_nonexistent_user():
    """トークンは有効だがユーザーが存在しない場合のテストです。"""
    from app.core.config import settings
    
    # get_user_by_usernameをモック化して存在しないユーザーをシミュレート
    with patch.object(
        User, 'get_user_by_username', new_callable=AsyncMock
    ) as mock_get_user:
        mock_get_user.return_value = None
        
        # 有効なトークンの生成
        token = create_access_token({"sub": "nonexistent_user"})
        
        # 存在しないユーザーでの認証実行
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token)
        
        # エラーの検証
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Could not validate credentials"
        mock_get_user.assert_called_once_with(username="nonexistent_user")


@pytest.mark.asyncio
async def test_get_current_user_missing_sub_claim():
    """subクレームが含まれていないトークンでの認証失敗をテストします。"""
    from app.core.config import settings
    
    # subクレームのない有効なトークンの生成
    token = create_access_token({"data": "no_sub_claim"})
    
    # 認証実行
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)
    
    # エラーの検証
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"
