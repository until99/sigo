from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DashboardBase(BaseModel):
    dashboardId: str
    dashboardName: str
    workspaceId: str
    workspaceName: Optional[str] = None
    groupId: Optional[int] = None
    groupName: Optional[str] = None
    groupDescription: Optional[str] = None
    backgroundImage: Optional[str] = None
    pipelineId: Optional[str] = None


class DashboardResponse(DashboardBase):
    createdAt: datetime

    class Config:
        from_attributes = True


class DashboardCreate(BaseModel):
    workspaceId: str = Field(..., min_length=1)
    dashboardId: str = Field(..., min_length=1)
    groupId: Optional[int] = None
    backgroundImage: Optional[str] = None
    pipelineId: Optional[str] = None


class DashboardUpdate(BaseModel):
    groupId: Optional[int] = None
    backgroundImage: Optional[str] = None
    pipelineId: Optional[str] = None


class DashboardRefreshRequest(BaseModel):
    workspaceId: str = Field(..., min_length=1)
    dashboardId: str = Field(..., min_length=1)


class DashboardRefreshStatusResponse(BaseModel):
    remainRefreshCount: int
    lastUpdatedAt: Optional[datetime] = None
