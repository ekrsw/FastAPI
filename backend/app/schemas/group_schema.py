from pydantic import BaseModel, ConfigDict, field_validator


class GroupBase(BaseModel):
    groupname: str

    @field_validator("groupname")
    def groupname_valid(cls, groupname):
        if not groupname.strip():
            raise ValueError("groupname must not be empty")
        if len(groupname) < 3 or len(groupname) > 100:
            raise ValueError("groupname must be between 3 and 100 characters")
        return groupname

class GroupCreate(GroupBase):
    pass

class GroupSchema(GroupBase):
    id: str
    
    model_config = ConfigDict(from_attributes=True)