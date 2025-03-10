from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.core import auth
from app.models.user import User
from app.schemas.user_schema import UserResponse


router = APIRouter(
    prefix="/users",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=UserResponse)
async def create_user(username: str, password: str, is_admin: bool=False) -> UserResponse:
    """
    新しいユーザーを登録します。

    このエンドポイントは、提供されたユーザー情報を基に新しいユーザーをデータベースに作成します。
    ユーザー名が既に登録されている場合はエラーを返します。
    認証不要でアクセスできます。

    Parameters
    ----------
    username : str
        作成するユーザー名。
    password : 
        作成するユーザーのパスワード。
    is_admin : bool
        作成するユーザーの管理者権限の有無。デフォルトはFalse。
    Returns
    -------
    UserResponse
        取得したユーザーの詳細を含むレスポンスモデル。

    Raises
    ------
    HTTPException
        ユーザーが存在しない場合に404 Not Foundエラーを返します。
    """
    # usernameで既存のユーザーを取得
    exit_user = await User.get_user_by_username(username)
    if exit_user:
        # 既存のユーザーが存在する場合はエラーを返す
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = await User.create_user(username, password, is_admin)
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

from fastapi import Body

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    username: str = Body(...),
    is_admin: bool = Body(None),
    current_user: User = Depends(auth.get_current_user)
    ) -> UserResponse:
    """
    指定されたユーザーの情報を更新します。

    このエンドポイントは、指定されたユーザーの情報を更新します。
    認証されたユーザーかつ自分自身か、管理者のみがアクセスできます。
    管理者権限の変更は管理者のみが実行できます。

    Parameters
    ----------
    user_id : int
        更新するユーザーのID。
    username : str
        更新するユーザーの名前。
    is_admin : bool
        更新するユーザーの管理者権限の有無。デフォルトはNone。
    Returns
    -------
    UserResponse
        更新したユーザーの詳細を含むレスポンスモデル。

    Raises
    ------
    HTTPException
        ユーザーが存在しない場合に404 Not Foundエラーを返します。
    """
    user = await User.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 自分自身か管理者のみがアクセス可能
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions. Only the user themselves or an admin can update user information. "
        )

    # 管理者権限の変更は管理者のみが実行可能
    if is_admin is not None and is_admin != user.is_admin and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions. Only admins can change admin privileges."
        )
    
    await User.update_user(user_id, username, is_admin)
    return await User.get_user_by_id(user_id)

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

    Raises
    ------
    HTTPException
        ユーザーが存在しない場合に404 Not Foundエラーを返します。
    """
    user = await User.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 管理者のみがアクセス可能
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions. Only admins can delete users."
        )
    await User.delete_user(user_id)
    return {"message": "User deleted successfully"}
