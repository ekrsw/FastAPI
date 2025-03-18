from pydantic import BaseModel, ConfigDict

class GroupCreate(BaseModel):
    groupname: str

class GroupSchema(BaseModel):
    id: int
    groupname: str
    
    model_config = ConfigDict(from_attributes=True)