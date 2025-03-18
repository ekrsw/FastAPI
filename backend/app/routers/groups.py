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
    new_group = await Group.from_schema(schema=group_in)
    return new_group