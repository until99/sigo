from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: str
    userBusinessArea: str
    userProfilePicture: Optional[str] = None
    isActive: bool = True


class UserCreate(UserBase):
    hashedPassword: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    userBusinessArea: Optional[str] = None
    userProfilePicture: Optional[str] = None
    isActive: Optional[bool] = None
    hashedPassword: Optional[str] = None


class User(UserBase):
    userId: int
    lastUpdatedAt: str
    createdAt: str

    class Config:
        orm_mode = True
