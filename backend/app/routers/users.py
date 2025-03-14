from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException

from app.core import auth
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate


router = APIRouter(
    prefix="/users",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=UserResponse)
async def create_user(user_in: UserCreate) -> UserResponse:
    """
    新しいユーザーを登録します。

    このエンドポイントは、提供されたユーザー情報を基に新しいユーザーをデータベースに作成します。
    ユーザー名が既に登録されている場合はエラーを返します。
    認証不要でアクセスできます。

    Parameters
    ----------
    user_in : UserCreate
        作成するユーザーの情報。
    Returns
    -------
    UserResponse
        作成したユーザーの詳細を含むレスポンスモデル。

    Raises
    ------
    HTTPException
        ユーザー名が既に存在する場合に400 Bad Requestエラーを返します。
    """
    # usernameで既存のユーザーを取得
    exit_user = await User.get_user_by_username(username=user_in.username)
    if exit_user:
        # 既存のユーザーが存在する場合はエラーを返す
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = await User.from_schema(schema=user_in)
    return new_user

@router.get("/{user_id}", response_model=UserResponse)
async def read_user_by_id(
    user_id: int,
    current_user: User=Depends(auth.get_current_user)
    ) -> UserResponse:
    """
    指定されたユーザーの情報を取得します。

    このエンドポイントは、指定されたユーザーの情報を取得します。
    認証されたユーザーのみがアクセスできます。

    Parameters
    ----------
    user_id : int
        取得するユーザーのID。
    current_user : User
        現在認証されているユーザー。

    Returns
    -------
    UserResponse
        取得したユーザーの詳細を含むレスポンスモデル。

    Raises
    ------
    HTTPException
        - ユーザーが存在しない場合に404 Not Foundエラーを返します。
        - 認証されていない場合に401 Unauthorizedエラーを返します。
    """
    user = await User.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/name/{username}", response_model=UserResponse)
async def read_user_by_username(
    username: str,
    current_user: User=Depends(auth.get_current_user)
    ) -> UserResponse:
    """
    指定されたユーザーの情報を取得します。

    このエンドポイントは、指定されたユーザーの情報を取得します。
    認証されたユーザーのみがアクセスできます。

    Parameters
    ----------
    username : str
        取得するユーザーの名前。
    Returns
    -------
    UserResponse
        取得したユーザーの詳細を含むレスポンスモデル。

    Raises
    ------
    HTTPException
        - ユーザーが存在しない場合に404 Not Foundエラーを返します。
        - 認証されていない場合に401 Unauthorizedエラーを返します。
    """
    user = await User.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=List[UserResponse])
async def read_all_users(current_user: User=Depends(auth.get_current_user)) -> List[UserResponse]:
    """
    全てのユーザーの情報を取得します。

    このエンドポイントは、全てのユーザーの情報を取得します。
    認証されたユーザーのみがアクセスできます。

    Returns
    -------
    List[UserResponse]
        取得した全てのユーザーの詳細を含むレスポンスモデル。
    """
    users = await User.get_all_users()
    if not users:
        users = []  # 空のリストを返す（404エラーは返さない）
    return [UserResponse.model_validate(user) for user in users]  # SQLAlchemyモデルをPydanticモデルに変換

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    *,
    user_in: UserUpdate,
    current_user: User = Depends(auth.get_current_user)
    ) -> UserResponse:
    """
    現在のユーザー情報を更新します。

    このエンドポイントは、現在認証されているユーザーの情報を更新します。
    管理者権限の変更はできません。

    Parameters
    ----------
    user_in : UserUpdate
        更新するユーザー情報。
    current_user : User
        現在認証されているユーザー。

    Returns
    -------
    UserResponse
        更新したユーザーの詳細を含むレスポンスモデル。

    Raises
    ------
    HTTPException
        管理者権限の変更を試みた場合に403 Forbiddenエラーを返します。
    """
    # 管理者権限の変更を防ぐ
    if user_in.is_admin is not None and user_in.is_admin != current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions. Only admins can change admin privileges."
        )
    
    # 更新実行
    updated_user = await User.update_from_schema(db_obj=current_user, schema=user_in)
    return updated_user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    *,
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(auth.get_current_user)
    ) -> UserResponse:
    """
    指定されたユーザーの情報を更新します。

    このエンドポイントは、指定されたユーザーの情報を更新します。
    管理者のみがアクセスできます。

    Parameters
    ----------
    user_id : int
        更新するユーザーのID。
    user_in : UserUpdate
        更新するユーザー情報。
    current_user : User
        現在認証されているユーザー。

    Returns
    -------
    UserResponse
        更新したユーザーの詳細を含むレスポンスモデル。

    Raises
    ------
    HTTPException
        - ユーザーが存在しない場合に404 Not Foundエラーを返します。
        - 管理者でない場合に403 Forbiddenエラーを返します。
    """
    # 管理者権限チェック
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions. Only admins can update other users."
        )
    
    # ユーザー存在チェック
    user = await User.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # 更新実行
    try:
        updated_user = await User.update_from_schema(db_obj=user, schema=user_in)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User=Depends(auth.get_current_user)
    ) -> dict:
    """
    指定されたユーザーを削除します。

    このエンドポイントは、指定されたユーザーを削除します。
    認証されたユーザーかつ管理者のみがアクセスできます。

    Parameters
    ----------
    user_id : int
        削除するユーザーのID。

    Returns
    -------
    dict
        削除成功メッセージを含む辞書。

    Raises
    ------
    HTTPException
        - ユーザーが存在しない場合に404 Not Foundエラーを返します。
        - 管理者でない場合に403 Forbiddenエラーを返します。
    """
    # ユーザー存在チェック
    user = await User.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 管理者権限チェック
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions. Only admins can delete users."
        )
    
    # 削除実行
    await User.delete_user(user_id)
    return {"message": "User deleted successfully"}
