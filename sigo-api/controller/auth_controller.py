from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

from models.user import User

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthController:
    """Controller responsible for authentication business logic."""

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password.

        Args:
            db: Database session
            email: User email
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        if not user.isActive:
            return None

        if not user.verify_password(password):
            return None

        return user

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token.

        Args:
            data: Data to encode in token
            expires_delta: Token expiration time

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    @staticmethod
    def login(db: Session, email: str, password: str) -> Optional[dict]:
        """Process user login.

        Args:
            db: Database session
            email: User email
            password: Plain text password

        Returns:
            Dictionary with access token and user data if successful, None otherwise
        """
        user = AuthController.authenticate_user(db, email, password)

        if not user:
            return None

        access_token = AuthController.create_access_token(
            data={"sub": user.email, "user_id": user.userId}
        )

        return {"access_token": access_token, "token_type": "bearer", "user": user}
