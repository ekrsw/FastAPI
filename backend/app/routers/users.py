from fastapi import APIRouter, HTTPException

from app.models.user import User
from app.schemas.user_schema import UserResponse


router = APIRouter(
    prefix="/user",
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
async def read_user_by_id(user_id: int) -> UserResponse:
    """
    指定されたユーザーの情報を取得します。

    このエンドポイントは、指定されたユーザーの情報を取得します。
    認証不要でアクセスできます。

    Parameters
    ----------
    user_id : int
        取得するユーザーのID。
    Returns
    -------
    UserResponse
        取得したユーザーの詳細を含むレスポンスモデル。

    Raises
    ------
    HTTPException
        ユーザーが存在しない場合に404 Not Foundエラーを返します。
    """
    user = await User.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{username}", response_model=UserResponse)
async def read_user_by_username(username: str) -> UserResponse:
    """
    指定されたユーザーの情報を取得します。

    このエンドポイントは、指定されたユーザーの情報を取得します。
    認証不要でアクセスできます。

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
        ユーザーが存在しない場合に404 Not Foundエラーを返します。
    """
    user = await User.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=UserResponse)
async def read_all_users() -> UserResponse:
    """
    全てのユーザーの情報を取得します。

    このエンドポイントは、全てのユーザーの情報を取得します。
    認証不要でアクセスできます。

    Returns
    -------
    UserResponse
        取得した全てのユーザーの詳細を含むレスポンスモデル。
    """
    users = await User.get_all_users()
    if not users:
        raise HTTPException(status_code=404, detail="Users not found")
    return users

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, username: str, is_admin: bool=None) -> UserResponse:
    """
    指定されたユーザーの情報を更新します。

    このエンドポイントは、指定されたユーザーの情報を更新します。
    認証不要でアクセスできます。

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
    await User.update_user(user_id, username, is_admin)
    return await User.get_user_by_id(user_id)

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    """
    指定されたユーザーを削除します。

    このエンドポイントは、指定されたユーザーを削除します。
    認証不要でアクセスできます。

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
    await User.delete_user(user_id)
    return {"message": "User deleted successfully"}
