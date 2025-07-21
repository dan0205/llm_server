""" from pydantic import BaseModel, EmailStr
from typing import Optional

class GoogleToken(BaseModel):
    token: str

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    google_sub: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
 """