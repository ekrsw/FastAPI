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
