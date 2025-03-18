from pydantic import BaseModel

class GroupCreate(BaseModel):
    groupname: str

class GroupSchema(BaseModel):
    id: int
    groupname: str