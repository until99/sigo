from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


from ..database import Base


class User(Base):
    __tablename__ = "sigo_users"
    userId = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    hashedPassword = Column(String)
    email = Column(String, unique=True, index=True)
    userBusinessArea = Column(String, index=True)
    userProfilePicture = Column(String, index=True)
    isActive = Column(Boolean, default=True)
    lastUpdatedAt = Column(String, index=True)
    createdAt = Column(String, index=True)
