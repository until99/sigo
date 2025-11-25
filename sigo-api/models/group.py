from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


# Association table for many-to-many relationship between users and groups
user_groups = Table(
    "user_groups",
    Base.metadata,
    Column(
        "userId",
        Integer,
        ForeignKey("sigo_users.userId", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "groupId",
        Integer,
        ForeignKey("sigo_groups.groupId", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("joinedAt", DateTime(timezone=True), server_default=func.now()),
)


class Group(Base):
    __tablename__ = "sigo_groups"

    groupId = Column(Integer, primary_key=True, index=True)
    groupName = Column(String, unique=True, index=True, nullable=False)
    groupDescription = Column(String)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    lastUpdatedAt = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with users (many-to-many)
    users = relationship("User", secondary=user_groups, back_populates="groups")
