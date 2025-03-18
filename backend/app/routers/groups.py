from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.core import auth
from app.models.group import Group
from app.models.user import User
from app.schemas.group_schema import GroupCreate, GroupSchema


router = APIRouter(
    prefix="/groups",
    tags=["group"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=GroupSchema)
async def create_group(
    group_in: GroupCreate,
    current_user: User=Depends(auth.get_current_user)
    ) -> GroupSchema:
    """新しいグループを作成します。

    このエンドポイントは、提供されたグループ情報を基に新しいグループをデータベースに作成します。
    認証されたユーザーのみがアクセスできます。

    Args:
        group_in (GroupCreate): 作成するグループの情報
        current_user (User): 現在認証されているユーザー

    Returns:
        GroupSchema: 作成したグループの詳細を含むレスポンスモデル（データベースにはまだcommitされていない状態）
    """
    new_group = await Group.from_schema(schema=group_in)
    return new_group

@router.get("/{group_id}", response_model=GroupSchema)
async def read_group_by_id(
    group_id: int,
    current_user: User=Depends(auth.get_current_user)
    ) -> GroupSchema:
    """指定されたグループの情報を取得します。

    このエンドポイントは、指定されたIDのグループ情報を取得します。
    認証されたユーザーのみがアクセスできます。

    Args:
        group_id (int): 取得するグループのID
        current_user (User): 現在認証されているユーザー

    Returns:
        GroupSchema: 取得したグループの詳細を含むレスポンスモデル

    Raises:
        HTTPException: グループが存在しない場合に404 Not Foundエラーを返します
    """
    group = await Group.get_group_by_id(group_id=group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.get("/", response_model=List[GroupSchema])
async def read_all_groups(
    current_user: User=Depends(auth.get_current_user)
    ) -> List[GroupSchema]:
    """全てのグループの情報を取得します。

    このエンドポイントは、全てのグループの情報を取得します。
    認証されたユーザーのみがアクセスできます。

    Args:
        current_user (User): 現在認証されているユーザー

    Returns:
        List[GroupSchema]: 取得した全てのグループの詳細を含むレスポンスモデルのリスト
    """
    groups = await Group.get_all_groups()
    if not groups:
        groups = []
    return [GroupSchema.model_validate(group) for group in groups]

@router.put("/{group_id}", response_model=GroupSchema)
async def update_group(
    group_id: int,
    group_in: GroupCreate,
    current_user: User=Depends(auth.get_current_user)
    ) -> GroupSchema:
    """指定されたグループの情報を更新します。

    このエンドポイントは、指定されたIDのグループ情報を更新します。
    認証されたユーザーのみがアクセスできます。
    管理者権限のチェックは行われません。

    Args:
        group_id (int): 更新するグループのID
        group_in (GroupCreate): 更新するグループ情報
        current_user (User): 現在認証されているユーザー

    Returns:
        GroupSchema: 更新したグループの詳細を含むレスポンスモデル

    Raises:
        HTTPException: 
            - グループが存在しない場合に404 Not Foundエラーを返します
            - 更新処理中にValueErrorが発生した場合に404エラーを返します
    """
    group = await Group.get_group_by_id(group_id=group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    try:
        updated_group = await Group.update_from_schema(db_obj=group, schema=group_in)
        return updated_group
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{group_id}")
async def delete_group(
    group_id: int,
    current_user: User=Depends(auth.get_current_user)
    ) -> dict:
    """指定されたグループを削除します。

    このエンドポイントは、指定されたIDのグループを物理削除します。
    認証されたユーザーかつ管理者のみがアクセスできます。

    Args:
        group_id (int): 削除するグループのID
        current_user (User): 現在認証されているユーザー

    Returns:
        dict: 削除成功メッセージを含む辞書

    Raises:
        HTTPException: 
            - グループが存在しない場合に404 Not Foundエラーを返します
            - 管理者でない場合に403 Forbiddenエラーを返します
    """
    # グループ存在チェック
    group = await Group.get_group_by_id(group_id=group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # 管理者権限チェック
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions. Only admins can delete groups."
        )
    
    # グループ削除実行
    await Group.delete_group_permanently(group_id=group_id)
    return {"message": "Group deleted successfully"}
