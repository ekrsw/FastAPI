from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import (
    Token, 
    authenticate_user, 
    create_access_token, 
    create_refresh_token,
    get_current_user
)
from app.models.user import User


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"description": "Unauthorized"}},
)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    アクセストークンを取得するためのログインエンドポイント

    このエンドポイントは、ユーザー名とパスワードを検証し、
    有効な場合はアクセストークンとリフレッシュトークンを返します。

    Parameters
    ----------
    form_data : OAuth2PasswordRequestForm, optional
        ユーザー名とパスワードを含むフォームデータ, by default Depends()

    Returns
    -------
    Token
        アクセストークンとリフレッシュトークンを含むトークンモデル

    Raises
    ------
    HTTPException
        認証に失敗した場合
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ユーザー名をサブジェクトとしてトークンを作成
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    リフレッシュトークンを使用して新しいアクセストークンを取得する

    このエンドポイントは、現在のユーザーの情報を使用して
    新しいアクセストークンとリフレッシュトークンを生成します。

    Parameters
    ----------
    current_user : User, optional
        現在のユーザー, by default Depends(get_current_user)

    Returns
    -------
    Token
        新しいアクセストークンとリフレッシュトークンを含むトークンモデル
    """
    # 新しいトークンを作成（ランダム性を追加して毎回異なるトークンを生成）
    import time
    import random
    
    # 現在のタイムスタンプとランダム値を追加して毎回異なるトークンを生成
    random_data = {
        "sub": current_user.username,
        "timestamp": time.time(),
        "random": random.random()
    }
    
    access_token = create_access_token(data=random_data)
    refresh_token = create_refresh_token(data=random_data)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=dict)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    現在のユーザー情報を取得する

    このエンドポイントは、現在認証されているユーザーの情報を返します。

    Parameters
    ----------
    current_user : User, optional
        現在のユーザー, by default Depends(get_current_user)

    Returns
    -------
    dict
        ユーザー情報を含む辞書
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin
    }
