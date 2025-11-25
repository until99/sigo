from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from controller.group_controller import GroupController
from schemas.group_schema import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupWithUsersResponse,
    AddUserToGroupRequest,
    RemoveUserFromGroupRequest,
)
from database import get_db

router_group = APIRouter()


# ==================== GROUP CRUD ROUTES ====================


@router_group.post(
    "/group",
    response_model=GroupResponse,
    summary="Create a new group",
    status_code=status.HTTP_201_CREATED,
)
def create_group(
    group_data: GroupCreate, db: Session = Depends(get_db)
) -> GroupResponse:
    """Create a new group.

    Args:
        group_data: Group creation data
        db: Database session dependency

    Returns:
        Created group data

    Raises:
        HTTPException: If group name already exists
    """
    group = GroupController.create_group(db, group_data)
    return GroupResponse.from_orm(group)


@router_group.get(
    "/group/{group_id}",
    response_model=GroupWithUsersResponse,
    summary="Get group by ID",
)
def get_group(group_id: int, db: Session = Depends(get_db)) -> GroupWithUsersResponse:
    """Get group by ID with its users.

    Args:
        group_id: Group ID
        db: Database session dependency

    Returns:
        Group data with list of users

    Raises:
        HTTPException: If group not found
    """
    group = GroupController.get_group_by_id(db, group_id)

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
        )

    return GroupWithUsersResponse.from_orm(group)


@router_group.get(
    "/group",
    response_model=List[GroupResponse],
    summary="Get all groups",
)
def get_groups(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[GroupResponse]:
    """Get list of groups with pagination.

    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        db: Database session dependency

    Returns:
        List of groups
    """
    groups = GroupController.get_groups(db, skip=skip, limit=limit)
    return [GroupResponse.from_orm(group) for group in groups]


@router_group.patch(
    "/group/{group_id}",
    response_model=GroupResponse,
    summary="Update group",
)
def update_group(
    group_id: int, group_data: GroupUpdate, db: Session = Depends(get_db)
) -> GroupResponse:
    """Update group information.

    Args:
        group_id: Group ID
        group_data: Group update data
        db: Database session dependency

    Returns:
        Updated group data

    Raises:
        HTTPException: If group not found or group name already exists
    """
    group = GroupController.update_group(db, group_id, group_data)

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
        )

    return GroupResponse.from_orm(group)


@router_group.delete(
    "/group/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete group",
)
def delete_group(group_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a group.

    Args:
        group_id: Group ID
        db: Database session dependency

    Raises:
        HTTPException: If group not found
    """
    success = GroupController.delete_group(db, group_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
        )


# ==================== USER-GROUP RELATIONSHIP ROUTES ====================


@router_group.get(
    "/user/{user_id}/groups",
    response_model=List[GroupResponse],
    summary="Get all groups user belongs to",
)
def get_user_groups(user_id: int, db: Session = Depends(get_db)) -> List[GroupResponse]:
    """Get all groups that a user belongs to.

    Args:
        user_id: User ID
        db: Database session dependency

    Returns:
        List of groups the user is a member of

    Raises:
        HTTPException: If user not found
    """
    groups = GroupController.get_user_groups(db, user_id)
    return [GroupResponse.from_orm(group) for group in groups]


@router_group.post(
    "/user/{user_id}/groups",
    status_code=status.HTTP_200_OK,
    summary="Add user to a group",
)
def add_user_to_group(
    user_id: int,
    request_data: AddUserToGroupRequest,
    db: Session = Depends(get_db),
):
def add_user_to_group(
    user_id: int,
    request_data: AddUserToGroupRequest,
    db: Session = Depends(get_db),
):
    """Add a user to a group.

    Args:
        user_id: User ID
        request_data: Request containing group ID
        db: Database session dependency

    Returns:
        Success message

    Raises:
        HTTPException: If group or user not found, or user already in group
    """
    GroupController.add_user_to_group(db, request_data.groupId, user_id)
    return {"message": "User added to group successfully"}


@router_group.delete(
    "/user/{user_id}/groups/{group_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove user from group",
)
def remove_user_from_group(
    user_id: int, group_id: int, db: Session = Depends(get_db)
):
    """Remove a user from a group.

    Args:
        user_id: User ID
        group_id: Group ID
        db: Database session dependency

    Returns:
        Success message

    Raises:
        HTTPException: If group or user not found, or user not in group
    """
    GroupController.remove_user_from_group(db, group_id, user_id)
    return {"message": "User removed from group successfully"}
