from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from controller.dashboard_controller import DashboardController
from schemas.dashboard_schema import (
    DashboardResponse,
    DashboardRefreshRequest,
    DashboardRefreshStatusResponse,
)
from database import get_db

router_dashboard = APIRouter()


# ==================== DASHBOARD ROUTES ====================


@router_dashboard.get(
    "/powerbi/dashboards",
    response_model=List[DashboardResponse],
    summary="Retrieve all dashboards from local database",
)
def get_all_dashboards(db: Session = Depends(get_db)) -> List[DashboardResponse]:
    """Retrieve all dashboards stored in the local database with group information.
    
    This endpoint returns dashboards that have been previously synced from Power BI.
    To sync new dashboards from Power BI, use the POST /powerbi/sync endpoint first.

    Args:
        db: Database session dependency

    Returns:
        List of all dashboards from local database

    Raises:
        HTTPException: If error occurs
    """
    controller = DashboardController()
    dashboards = controller.get_all_dashboards(db)
    
    # Enrich with group information
    response = []
    for dashboard in dashboards:
        dashboard_dict = {
            "dashboardId": dashboard.dashboardId,
            "dashboardName": dashboard.dashboardName,
            "workspaceId": dashboard.workspaceId,
            "workspaceName": dashboard.workspaceName,
            "groupId": dashboard.groupId,
            "groupName": dashboard.group.groupName if dashboard.group else None,
            "groupDescription": dashboard.group.groupDescription if dashboard.group else None,
            "backgroundImage": dashboard.backgroundImage,
            "pipelineId": dashboard.pipelineId,
            "createdAt": dashboard.createdAt,
        }
        response.append(DashboardResponse(**dashboard_dict))
    
    return response


@router_dashboard.get(
    "/powerbi/workspace/{workspace_id}/dashboard/{dashboard_id}",
    response_model=DashboardResponse,
    summary="Retrieve specific dashboard within a workspace",
)
def get_dashboard(
    workspace_id: str, dashboard_id: str, db: Session = Depends(get_db)
) -> DashboardResponse:
    """Get a specific dashboard by workspace and dashboard ID.

    Args:
        workspace_id: Workspace ID
        dashboard_id: Dashboard ID
        db: Database session dependency

    Returns:
        Dashboard data

    Raises:
        HTTPException: If dashboard not found
    """
    controller = DashboardController()
    dashboard = controller.get_dashboard_by_id(db, workspace_id, dashboard_id)

    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found"
        )

    dashboard_dict = {
        "dashboardId": dashboard.dashboardId,
        "dashboardName": dashboard.dashboardName,
        "workspaceId": dashboard.workspaceId,
        "workspaceName": dashboard.workspaceName,
        "groupId": dashboard.groupId,
        "groupName": dashboard.group.groupName if dashboard.group else None,
        "groupDescription": dashboard.group.groupDescription if dashboard.group else None,
        "backgroundImage": dashboard.backgroundImage,
        "pipelineId": dashboard.pipelineId,
        "createdAt": dashboard.createdAt,
    }

    return DashboardResponse(**dashboard_dict)


@router_dashboard.delete(
    "/powerbi/dashboard/{dashboard_id}",
    summary="Delete a dashboard",
)
def delete_dashboard(
    dashboard_id: str,
    request_data: dict,
    db: Session = Depends(get_db),
):
    """Delete a dashboard from Power BI and database.

    Args:
        dashboard_id: Dashboard ID
        request_data: Request containing workspaceId
        db: Database session dependency

    Returns:
        Success message

    Raises:
        HTTPException: If dashboard not found or deletion fails
    """
    workspace_id = request_data.get("workspaceId")
    if not workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="workspaceId is required",
        )

    controller = DashboardController()
    controller.delete_dashboard(db, workspace_id, dashboard_id)

    return {"message": "Dashboard deleted successfully"}


@router_dashboard.get(
    "/powerbi/dashboards/group/{group_id}",
    response_model=List[DashboardResponse],
    summary="Retrieve all dashboards within a specific group",
)
def get_group_dashboards(
    group_id: int, db: Session = Depends(get_db)
) -> List[DashboardResponse]:
    """Get all dashboards in a specific group.

    Args:
        group_id: Group ID
        db: Database session dependency

    Returns:
        List of dashboards in the group

    Raises:
        HTTPException: If group not found
    """
    controller = DashboardController()
    dashboards = controller.get_dashboards_by_group(db, group_id)

    response = []
    for dashboard in dashboards:
        dashboard_dict = {
            "dashboardId": dashboard.dashboardId,
            "dashboardName": dashboard.dashboardName,
            "workspaceId": dashboard.workspaceId,
            "workspaceName": dashboard.workspaceName,
            "groupId": dashboard.groupId,
            "groupName": dashboard.group.groupName if dashboard.group else None,
            "groupDescription": dashboard.group.groupDescription if dashboard.group else None,
            "backgroundImage": dashboard.backgroundImage,
            "pipelineId": dashboard.pipelineId,
            "createdAt": dashboard.createdAt,
        }
        response.append(DashboardResponse(**dashboard_dict))

    return response


@router_dashboard.post(
    "/powerbi/dashboard/refresh",
    summary="Trigger a refresh for a dashboard",
)
def refresh_dashboard(request_data: DashboardRefreshRequest):
    """Trigger a dataset refresh for a dashboard.

    Args:
        request_data: Request containing workspaceId and dashboardId

    Returns:
        Success message

    Raises:
        HTTPException: If refresh fails
    """
    controller = DashboardController()
    
    # Note: This requires the dataset ID, which should be obtained from the dashboard
    # For now, we'll use the dashboard_id as dataset_id
    # In production, you should map dashboard to its dataset
    controller.refresh_dashboard_dataset(
        request_data.workspaceId, request_data.dashboardId
    )

    return {"message": "Refresh started successfully"}


@router_dashboard.get(
    "/powerbi/dashboard/refresh-status",
    response_model=DashboardRefreshStatusResponse,
    summary="Retrieve remaining refresh count and status",
)
def get_refresh_status(
    workspace_id: str, dataset_id: str
) -> DashboardRefreshStatusResponse:
    """Get refresh status for a dataset.

    Args:
        workspace_id: Workspace ID (query parameter)
        dataset_id: Dataset ID (query parameter)

    Returns:
        Refresh status information

    Raises:
        HTTPException: If error occurs
    """
    controller = DashboardController()
    status_data = controller.get_dataset_refresh_status(workspace_id, dataset_id)

    return DashboardRefreshStatusResponse(**status_data)


@router_dashboard.post(
    "/powerbi/sync",
    summary="Sync dashboards from Power BI to local database",
)
def sync_dashboards(db: Session = Depends(get_db)):
    """Sync all dashboards from Power BI platform to local database.
    
    This endpoint:
    1. Connects to Power BI using configured credentials
    2. Retrieves all workspaces and their dashboards
    3. Inserts new dashboards or updates existing ones in the local database
    
    Use this endpoint to:
    - Initial sync of all Power BI dashboards
    - Refresh dashboard list when new dashboards are created in Power BI
    - Update dashboard metadata (names, workspace info, etc.)

    Args:
        db: Database session dependency

    Returns:
        Success message with count of synced dashboards

    Raises:
        HTTPException: If sync fails (e.g., invalid credentials, API errors)
    """
    controller = DashboardController()
    dashboards = controller.sync_dashboards_from_powerbi(db)

    return {
        "message": "Dashboards synced successfully from Power BI",
        "count": len(dashboards),
        "dashboards": [
            {
                "dashboardId": d.dashboardId,
                "dashboardName": d.dashboardName,
                "workspaceId": d.workspaceId,
                "workspaceName": d.workspaceName,
            }
            for d in dashboards
        ],
    }
