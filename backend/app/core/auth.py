from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.models.user import User
from .config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def create_jwt_token(
        data: Dict[str, str],
        secret_key: str,
        algorithm: str,
        expires_delta: Optional[timedelta] = None
        ) -> str:
    """
    指定されたデータと有効期限を持つJSON Web Token (JWT) を作成します。

    Parameters
    ----------
    data : Dict[str, str]
        トークンに含めるペイロードデータ。
    secret_key : str
        トークンの署名に使用するシークレットキー。
    algorithm : str
        トークンのエンコーディングに使用するアルゴリズム。
    expires_delta : Optional[timedelta], optional
        トークンの有効期限を設定する時間差。指定しない場合は15分後に設定されます。

    Returns
    -------
    str
        エンコードされたJWT。
    """
    to_encode = data.copy()
    if expires_delta is None:
        expire = datetime.utcnow() + timedelta(minutes=15)
    else:
        expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)

def create_access_token(data: Dict[str, str], expires_delta: Optional[timedelta] = None) -> str:
    """
    指定されたペイロードと有効期限でアクセストークンを作成します。

    Parameters
    ----------
    data : Dict[str, str]
        アクセストークンに含めるペイロードデータ。
    expires_delta : Optional[timedelta], optional
        トークンの有効期限を設定する時間差。指定しない場合は設定ファイルの値が使用されます。

    Returns
    -------
    str
        エンコードされたアクセストークン。
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    return create_jwt_token(
        data,
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expires_delta=expires_delta
    )

def decode_token(token: str, secret_key: str, algorithms: List[str]) -> Dict:
    """
    JWTをデコードし、そのペイロードを返します。

    Parameters
    ----------
    token : str
        デコード対象のJWT。
    secret_key : str
        トークンのデコードに使用するシークレットキー。
    algorithms : List[str]
        デコードに許可されるアルゴリズムのリスト。

    Returns
    -------
    Dict
        デコードされたトークンのペイロード。
    """
    return jwt.decode(token, secret_key, algorithms=algorithms)

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    ユーザー名とパスワードを用いてユーザーを認証します。

    Parameters
    ----------
    db : AsyncSession
        ユーザーを取得するためのデータベースセッション。
    username : str
        認証を試みるユーザーのユーザー名。
    password : str
        ユーザーが提供したプレーンテキストパスワード。

    Returns
    -------
    Optional[schemas.User]
        認証に成功した場合はユーザーオブジェクトを返し、失敗した場合はNoneを返します。
    """
    user = await User.get_user_by_username(username)
    if not user or not User.verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[User]:
    """
    提供されたJWTに基づいて現在認証されているユーザーを取得します。

    Parameters
    ----------
    token : str, optional
        リクエストに含まれるJWT。OAuth2スキームを通じて取得されます。
    db : AsyncSession, optional
        データベースセッション。依存関係として取得されます。

    Raises
    ------
    HTTPException
        トークンが無効であるか、ユーザーが存在しない場合に発生します。

    Returns
    -------
    schemas.User
        認証されたユーザーオブジェクト。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token, settings.secret_key, [settings.algorithm])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await User.get_user_by_username(username=username)
    if user is None:
        raise credentials_exception
    return user