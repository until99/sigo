from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status

from models.group import Group
from models.user import User
from schemas.group_schema import GroupCreate, GroupUpdate


class GroupController:
    """Controller responsible for group management business logic."""

    @staticmethod
    def create_group(db: Session, group_data: GroupCreate) -> Group:
        """Create a new group.

        Args:
            db: Database session
            group_data: Group creation data

        Returns:
            Created Group object

        Raises:
            HTTPException: If group name already exists
        """
        existing_group = (
            db.query(Group).filter(Group.groupName == group_data.groupName).first()
        )

        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group name already exists",
            )

        db_group = Group(
            groupName=group_data.groupName,
            groupDescription=group_data.groupDescription,
            backgroundImage=group_data.backgroundImage,
        )

        db.add(db_group)
        db.commit()
        db.refresh(db_group)

        return db_group

    @staticmethod
    def get_group_by_id(db: Session, group_id: int) -> Optional[Group]:
        """Get group by ID.

        Args:
            db: Database session
            group_id: Group ID

        Returns:
            Group object if found, None otherwise
        """
        return db.query(Group).filter(Group.groupId == group_id).first()

    @staticmethod
    def get_group_by_name(db: Session, group_name: str) -> Optional[Group]:
        """Get group by name.

        Args:
            db: Database session
            group_name: Group name

        Returns:
            Group object if found, None otherwise
        """
        return db.query(Group).filter(Group.groupName == group_name).first()

    @staticmethod
    def get_groups(db: Session, skip: int = 0, limit: int = 100) -> List[Group]:
        """Get list of groups with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Group objects
        """
        return db.query(Group).offset(skip).limit(limit).all()

    @staticmethod
    def update_group(
        db: Session, group_id: int, group_data: GroupUpdate
    ) -> Optional[Group]:
        """Update group information.

        Args:
            db: Database session
            group_id: Group ID
            group_data: Group update data

        Returns:
            Updated Group object if found, None otherwise

        Raises:
            HTTPException: If group name already exists
        """
        db_group = db.query(Group).filter(Group.groupId == group_id).first()

        if not db_group:
            return None

        # Check if new group name already exists (if being updated)
        if group_data.groupName and group_data.groupName != db_group.groupName:
            existing_group = (
                db.query(Group).filter(Group.groupName == group_data.groupName).first()
            )

            if existing_group:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Group name already exists",
                )

        # Update fields if provided
        update_data = group_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_group, field, value)

        db.commit()
        db.refresh(db_group)

        return db_group

    @staticmethod
    def delete_group(db: Session, group_id: int) -> bool:
        """Delete a group.

        Args:
            db: Database session
            group_id: Group ID

        Returns:
            True if deleted, False if not found
        """
        db_group = db.query(Group).filter(Group.groupId == group_id).first()

        if not db_group:
            return False

        db.delete(db_group)
        db.commit()

        return True

    @staticmethod
    def add_user_to_group(db: Session, group_id: int, user_id: int) -> Group:
        """Add a user to a group.

        Args:
            db: Database session
            group_id: Group ID
            user_id: User ID

        Returns:
            Updated Group object

        Raises:
            HTTPException: If group or user not found, or user already in group
        """
        db_group = db.query(Group).filter(Group.groupId == group_id).first()
        if not db_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
            )

        db_user = db.query(User).filter(User.userId == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Check if user is already in the group
        if db_user in db_group.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this group",
            )

        db_group.users.append(db_user)
        db.commit()
        db.refresh(db_group)

        return db_group

    @staticmethod
    def remove_user_from_group(db: Session, group_id: int, user_id: int) -> Group:
        """Remove a user from a group.

        Args:
            db: Database session
            group_id: Group ID
            user_id: User ID

        Returns:
            Updated Group object

        Raises:
            HTTPException: If group or user not found, or user not in group
        """
        db_group = db.query(Group).filter(Group.groupId == group_id).first()
        if not db_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
            )

        db_user = db.query(User).filter(User.userId == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Check if user is in the group
        if db_user not in db_group.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a member of this group",
            )

        db_group.users.remove(db_user)
        db.commit()
        db.refresh(db_group)

        return db_group

    @staticmethod
    def get_user_groups(db: Session, user_id: int) -> List[Group]:
        """Get all groups that a user belongs to.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of Group objects

        Raises:
            HTTPException: If user not found
        """
        db_user = db.query(User).filter(User.userId == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return db_user.groups
