from pydantic import BaseModel, field_validator
from typing import List, Optional


class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    
    class Config:
        from_attributes = True

class UserSchema(BaseModel):
    username: str
    password: str
    is_admin: Optional[bool] = False

    @field_validator("username")
    def username_valid(cls, username):
        if username is not None:
            if not username.strip():
                raise ValueError("username must not be empty")
            if len(username) < 3 or len(username) > 50:
                raise ValueError("username must be between 3 and 50 characters")
        return username

    @field_validator("password")
    def password_valid(cls, password):
        if password is not None:
            if not password.strip():
                raise ValueError("password must not be empty")
            if len(password) < 8 or len(password) > 20:
                raise ValueError("password must be between 8 and 20 characters")
        return password
