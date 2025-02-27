from pydantic import BaseModel
from typing import List, Optional

class UserSchema(BaseModel):
    id: int
    username: str
    password: str
    created_at: str
    updated_at: str