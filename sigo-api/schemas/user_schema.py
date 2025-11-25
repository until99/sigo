from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    userBusinessArea: str
    userProfilePicture: Optional[str] = None
    isActive: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=1, max_length=16)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    userBusinessArea: Optional[str] = None
    userProfilePicture: Optional[str] = None
    isActive: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=1, max_length=16)


class UserResponse(UserBase):
    userId: int
    lastUpdatedAt: Optional[datetime] = None
    createdAt: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., max_length=16)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
