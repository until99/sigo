from sqlalchemy.orm import Session
from typing import Optional, List

from models.user import User
from schemas.user_schema import UserCreate, UserUpdate


class UserController:
    """Controller responsible for user management business logic."""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user.

        Args:
            db: Database session
            user_data: User creation data

        Returns:
            Created User object
        """
        hashed_password = User.hash_password(user_data.password)

        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashedPassword=hashed_password,
            userBusinessArea=user_data.userBusinessArea,
            userProfilePicture=user_data.userProfilePicture,
            isActive=user_data.isActive,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.userId == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            db: Database session
            email: User email

        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of User objects
        """
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information.

        Args:
            db: Database session
            user_id: User ID
            user_data: User update data

        Returns:
            Updated User object if found, None otherwise
        """
        db_user = db.query(User).filter(User.userId == user_id).first()

        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)

        # Handle password update separately
        if "password" in update_data:
            update_data["hashedPassword"] = User.hash_password(
                update_data.pop("password")
            )

        for key, value in update_data.items():
            setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user (soft delete by setting isActive to False).

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if user was deleted, False if not found
        """
        db_user = db.query(User).filter(User.userId == user_id).first()

        if not db_user:
            return False

        setattr(db_user, "isActive", False)
        db.commit()

        return True
