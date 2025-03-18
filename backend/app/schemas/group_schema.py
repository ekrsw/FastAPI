from pydantic import BaseModel

class GroupSchema(BaseModel):
    id: int
    groupname: str