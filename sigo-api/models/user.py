from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
import bcrypt

from database import Base


class User(Base):
    __tablename__ = "sigo_users"

    userId = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    hashedPassword = Column(String)
    email = Column(String, unique=True, index=True)
    userBusinessArea = Column(String, index=True)
    userProfilePicture = Column(String, index=True)
    isActive = Column(Boolean, default=True)
    lastUpdatedAt = Column(DateTime(timezone=True), onupdate=func.now())
    createdAt = Column(DateTime(timezone=True), server_default=func.now())

    def verify_password(self, plain_password: str) -> bool:
        """Verify if the provided password matches the hashed password."""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            self.hashedPassword.encode("utf-8")
            if isinstance(self.hashedPassword, str)
            else self.hashedPassword,
        )

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain password."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
