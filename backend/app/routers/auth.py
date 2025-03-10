from datetime import timedelta
import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core import auth, config
from app.schemas import auth_schema


ACCESS_TOKEN_EXPIRE_MINUTE = config.settings.jwt_access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTE = config.settings.jwt_refresh_token_expire_minutes

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"description": "Unauthorized"}},
)

@router.post("/token", response_model=auth_schema.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> auth_schema.Token:
    """
    アクセストークンとリフレッシュトークンを発行します。

    このエンドポイントは、ユーザーの認証情報を検証し、
    有効な場合はアクセストークンとリフレッシュトークンを発行します。

    Parameters
    ----------
    form_data : OAuth2PasswordRequestForm
        ユーザーが提供する認証情報（ユーザー名とパスワード）。
    db : AsyncSession
        データベースセッション。

    Returns
    -------
    schemas.Token
        アクセストークン、トークンタイプ、およびリフレッシュトークンを含むレスポンス。
    
    Raises
    ------
    HTTPException
        認証情報が不正な場合、401 Unauthorized エラーを返します。
    """
    # ユーザーの認証を試みる
    user = await auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # アクセストークンの有効期限を設定
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTE)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # リフレッシュトークンの有効期限を設定
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTE)
    refresh_token = auth.create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )
    
    # トークンを返す
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }
