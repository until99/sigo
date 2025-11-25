from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from controller.user_controller import UserController
from schemas.user_schema import UserCreate, UserUpdate, UserResponse
from database import get_db

router_user = APIRouter()


@router_user.post(
    "/users",
    response_model=UserResponse,
    summary="Create a new user",
    status_code=status.HTTP_201_CREATED,
)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """Create a new user.

    Args:
        user_data: User creation data
        db: Database session dependency

    Returns:
        Created user data

    Raises:
        HTTPException: If email already exists
    """
    existing_user = UserController.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    user = UserController.create_user(db, user_data)
    return UserResponse.from_orm(user)


@router_user.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    """Get user by ID.

    Args:
        user_id: User ID
        db: Database session dependency

    Returns:
        User data

    Raises:
        HTTPException: If user not found
    """
    user = UserController.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserResponse.from_orm(user)


@router_user.get(
    "/users",
    response_model=List[UserResponse],
    summary="Get list of users",
)
def get_users(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[UserResponse]:
    """Get list of users with pagination.

    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        db: Database session dependency

    Returns:
        List of users
    """
    users = UserController.get_users(db, skip=skip, limit=limit)
    return [UserResponse.from_orm(user) for user in users]


@router_user.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Update user",
)
def update_user(
    user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)
) -> UserResponse:
    """Update user information.

    Args:
        user_id: User ID
        user_data: User update data
        db: Database session dependency

    Returns:
        Updated user data

    Raises:
        HTTPException: If user not found
    """
    user = UserController.update_user(db, user_id, user_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserResponse.from_orm(user)


@router_user.delete(
    "/users/{user_id}",
    summary="Delete user",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    """Delete user (soft delete).

    Args:
        user_id: User ID
        db: Database session dependency

    Raises:
        HTTPException: If user not found
    """
    deleted = UserController.delete_user(db, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
