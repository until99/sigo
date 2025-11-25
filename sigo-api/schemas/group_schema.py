from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GroupBase(BaseModel):
    groupName: str = Field(..., min_length=1, max_length=255)
    groupDescription: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    groupName: Optional[str] = Field(None, min_length=1, max_length=255)
    groupDescription: Optional[str] = None


class GroupResponse(GroupBase):
    groupId: int
    createdAt: datetime
    lastUpdatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class GroupWithUsersResponse(GroupResponse):
    users: List["UserInGroupResponse"] = []


class UserInGroupResponse(BaseModel):
    userId: int
    username: str
    email: str
    userBusinessArea: str
    userProfilePicture: Optional[str] = None
    isActive: bool

    class Config:
        from_attributes = True


class AddUserToGroupRequest(BaseModel):
    userId: int = Field(..., gt=0)


class RemoveUserFromGroupRequest(BaseModel):
    userId: int = Field(..., gt=0)
