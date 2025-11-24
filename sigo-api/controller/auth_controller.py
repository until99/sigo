from models.user import User
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import Optional


class AuthController:
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    async def login(cls, db: Session, username: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.username == username).first()
        if user and user.verify_password(password):
            return user
        return None
