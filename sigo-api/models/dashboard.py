from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Dashboard(Base):
    __tablename__ = "sigo_dashboards"

    dashboardId = Column(String, primary_key=True, index=True)
    dashboardName = Column(String, nullable=False, index=True)
    workspaceId = Column(String, nullable=False, index=True)
    workspaceName = Column(String)
    groupId = Column(
        Integer, ForeignKey("sigo_groups.groupId", ondelete="SET NULL"), nullable=True
    )
    backgroundImage = Column(String)
    pipelineId = Column(String, nullable=True)
    embedUrl = Column(String)
    webUrl = Column(String)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    lastUpdatedAt = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with group
    group = relationship("Group", backref="dashboards")
