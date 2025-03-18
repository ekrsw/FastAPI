from fastapi import APIRouter

from app.models.group import Group


router = APIRouter(
    prefix="/groups",
    tags=["group"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=GroupResponse)
async def create_group(group_in: GroupCreate) -> GroupResponse:
    # グループ名で既存のグループを取得
    exist_group = await Group.get_group_by_groupname(groupname=group_in.groupname)
    if exist_group:
        #  既存のユーザーが存在する場合はエラーを返す
        raise HTTPException(status_code=404, detail="Group already exists")