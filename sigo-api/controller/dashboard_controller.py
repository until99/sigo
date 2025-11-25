from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status

from models.dashboard import Dashboard
from models.group import Group
from schemas.dashboard_schema import DashboardUpdate
from services.powerbi_service import PowerBIService


class DashboardController:
    """Controller responsible for dashboard management business logic."""

    def __init__(self):
        self.powerbi_service = PowerBIService()

    def get_all_dashboards(self, db: Session) -> List[Dashboard]:
        """Get all dashboards from database with group information.

        Args:
            db: Database session

        Returns:
            List of Dashboard objects
        """
        return db.query(Dashboard).all()

    def get_dashboard_by_id(
        self, db: Session, workspace_id: str, dashboard_id: str
    ) -> Optional[Dashboard]:
        """Get a specific dashboard from database.

        Args:
            db: Database session
            workspace_id: Workspace ID
            dashboard_id: Dashboard ID

        Returns:
            Dashboard object if found, None otherwise
        """
        return (
            db.query(Dashboard)
            .filter(
                Dashboard.dashboardId == dashboard_id,
                Dashboard.workspaceId == workspace_id,
            )
            .first()
        )

    def sync_dashboards_from_powerbi(self, db: Session) -> List[Dashboard]:
        """Sync all dashboards from Power BI to local database.

        Args:
            db: Database session

        Returns:
            List of synced Dashboard objects
        """
        try:
            # Get all workspaces
            workspaces = self.powerbi_service.get_workspaces()
            synced_dashboards = []

            for workspace in workspaces:
                workspace_id = workspace.get("id")
                workspace_name = workspace.get("name")

                # Get dashboards for this workspace
                try:
                    powerbi_dashboards = self.powerbi_service.get_workspace_dashboards(
                        workspace_id
                    )

                    for pbi_dashboard in powerbi_dashboards:
                        dashboard_id = pbi_dashboard.get("id")
                        dashboard_name = pbi_dashboard.get("displayName")

                        # Check if dashboard exists in database
                        db_dashboard = (
                            db.query(Dashboard)
                            .filter(Dashboard.dashboardId == dashboard_id)
                            .first()
                        )

                        if db_dashboard:
                            # Update existing dashboard
                            db_dashboard.dashboardName = dashboard_name
                            db_dashboard.workspaceName = workspace_name
                            db_dashboard.embedUrl = pbi_dashboard.get("embedUrl")
                            db_dashboard.webUrl = pbi_dashboard.get("webUrl")
                        else:
                            # Create new dashboard
                            db_dashboard = Dashboard(
                                dashboardId=dashboard_id,
                                dashboardName=dashboard_name,
                                workspaceId=workspace_id,
                                workspaceName=workspace_name,
                                embedUrl=pbi_dashboard.get("embedUrl"),
                                webUrl=pbi_dashboard.get("webUrl"),
                            )
                            db.add(db_dashboard)

                        synced_dashboards.append(db_dashboard)

                except Exception as e:
                    print(f"Error syncing dashboards from workspace {workspace_id}: {e}")
                    continue

            db.commit()
            return synced_dashboards

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error syncing dashboards from Power BI: {str(e)}",
            )

    def get_dashboard_from_powerbi(
        self, workspace_id: str, dashboard_id: str
    ) -> Dict[str, Any]:
        """Get dashboard details from Power BI API.

        Args:
            workspace_id: Workspace ID
            dashboard_id: Dashboard ID

        Returns:
            Dashboard data from Power BI

        Raises:
            HTTPException: If dashboard not found or API error
        """
        try:
            return self.powerbi_service.get_workspace_dashboard(
                workspace_id, dashboard_id
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dashboard not found in Power BI: {str(e)}",
            )

    def delete_dashboard(
        self, db: Session, workspace_id: str, dashboard_id: str
    ) -> bool:
        """Delete a dashboard from Power BI and database.

        Args:
            db: Database session
            workspace_id: Workspace ID
            dashboard_id: Dashboard ID

        Returns:
            True if deleted successfully

        Raises:
            HTTPException: If dashboard not found or deletion fails
        """
        # Delete from Power BI
        try:
            self.powerbi_service.delete_dashboard(workspace_id, dashboard_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting dashboard from Power BI: {str(e)}",
            )

        # Delete from database
        db_dashboard = (
            db.query(Dashboard)
            .filter(
                Dashboard.dashboardId == dashboard_id,
                Dashboard.workspaceId == workspace_id,
            )
            .first()
        )

        if db_dashboard:
            db.delete(db_dashboard)
            db.commit()

        return True

    def get_dashboards_by_group(self, db: Session, group_id: int) -> List[Dashboard]:
        """Get all dashboards in a specific group.

        Args:
            db: Database session
            group_id: Group ID

        Returns:
            List of Dashboard objects

        Raises:
            HTTPException: If group not found
        """
        # Verify group exists
        group = db.query(Group).filter(Group.groupId == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
            )

        return db.query(Dashboard).filter(Dashboard.groupId == group_id).all()

    def update_dashboard(
        self, db: Session, dashboard_id: str, dashboard_data: DashboardUpdate
    ) -> Optional[Dashboard]:
        """Update dashboard information in database.

        Args:
            db: Database session
            dashboard_id: Dashboard ID
            dashboard_data: Update data

        Returns:
            Updated Dashboard object

        Raises:
            HTTPException: If group not found (when updating groupId)
        """
        db_dashboard = (
            db.query(Dashboard).filter(Dashboard.dashboardId == dashboard_id).first()
        )

        if not db_dashboard:
            return None

        # Verify group exists if groupId is being updated
        if dashboard_data.groupId is not None:
            group = db.query(Group).filter(Group.groupId == dashboard_data.groupId).first()
            if not group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
                )

        # Update fields
        update_data = dashboard_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_dashboard, field, value)

        db.commit()
        db.refresh(db_dashboard)

        return db_dashboard

    def refresh_dashboard_dataset(self, workspace_id: str, dataset_id: str) -> bool:
        """Trigger a refresh for a dashboard's dataset.

        Args:
            workspace_id: Workspace ID
            dataset_id: Dataset ID

        Returns:
            True if refresh triggered successfully

        Raises:
            HTTPException: If refresh fails
        """
        try:
            return self.powerbi_service.refresh_dataset(workspace_id, dataset_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error triggering dataset refresh: {str(e)}",
            )

    def get_dataset_refresh_status(
        self, workspace_id: str, dataset_id: str
    ) -> Dict[str, Any]:
        """Get refresh status and history for a dataset.

        Args:
            workspace_id: Workspace ID
            dataset_id: Dataset ID

        Returns:
            Dictionary with refresh status information

        Raises:
            HTTPException: If error occurs
        """
        try:
            # Get refresh history
            refresh_history = self.powerbi_service.get_dataset_refresh_history(
                workspace_id, dataset_id
            )

            # Calculate remaining refresh count (assuming 8 refreshes per day for Pro)
            # This is a simplified calculation - actual limits depend on license type
            last_refresh = None
            if refresh_history:
                last_refresh = refresh_history[0].get("endTime")

            return {
                "remainRefreshCount": 8 - len(refresh_history),  # Simplified
                "lastUpdatedAt": last_refresh,
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting refresh status: {str(e)}",
            )
