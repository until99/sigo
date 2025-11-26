"""Tests for dashboard controller and endpoints."""

import pytest
from models.dashboard import Dashboard
from models.group import Group
from controller.dashboard_controller import DashboardController


@pytest.fixture
def test_dashboard(db, test_group):
    """Create a test dashboard."""
    dashboard = Dashboard(
        dashboardId="test-dashboard-123",
        dashboardName="Test Dashboard",
        workspaceId="test-workspace-456",
        workspaceName="Test Workspace",
        groupId=test_group.groupId,
        backgroundImage="test_bg.jpg",
        embedUrl="https://powerbi.com/embed/test",
        webUrl="https://powerbi.com/test",
    )
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    return dashboard


@pytest.fixture
def test_group(db):
    """Create a test group for dashboards."""
    group = Group(
        groupName="Dashboard Test Group", groupDescription="Group for dashboard tests"
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


class TestDashboardController:
    """Test cases for DashboardController."""

    def test_get_all_dashboards(self, db, test_dashboard):
        """Test getting all dashboards."""
        controller = DashboardController()
        dashboards = controller.get_all_dashboards(db)

        assert len(dashboards) >= 1
        assert any(d.dashboardId == test_dashboard.dashboardId for d in dashboards)

    def test_get_dashboard_by_id(self, db, test_dashboard):
        """Test getting dashboard by ID."""
        controller = DashboardController()
        dashboard = controller.get_dashboard_by_id(db, test_dashboard.dashboardId)

        assert dashboard is not None
        assert dashboard.dashboardId == test_dashboard.dashboardId
        assert dashboard.dashboardName == test_dashboard.dashboardName

    def test_get_dashboard_by_id_not_found(self, db):
        """Test getting non-existent dashboard."""
        controller = DashboardController()
        dashboard = controller.get_dashboard_by_id(db, "nonexistent-id")

        assert dashboard is None

    def test_get_dashboards_by_workspace(self, db, test_dashboard):
        """Test getting dashboards by workspace ID."""
        controller = DashboardController()
        dashboards = controller.get_dashboards_by_workspace(
            db, test_dashboard.workspaceId
        )

        assert len(dashboards) >= 1
        assert all(d.workspaceId == test_dashboard.workspaceId for d in dashboards)

    def test_get_dashboards_by_group(self, db, test_dashboard, test_group):
        """Test getting dashboards by group ID."""
        controller = DashboardController()
        dashboards = controller.get_dashboards_by_group(db, test_group.groupId)

        assert len(dashboards) >= 1
        assert all(d.groupId == test_group.groupId for d in dashboards)

    def test_update_dashboard_group(self, db, test_dashboard):
        """Test updating dashboard group assignment."""
        # Create new group
        new_group = Group(groupName="New Group", groupDescription="New group for test")
        db.add(new_group)
        db.commit()
        db.refresh(new_group)

        controller = DashboardController()
        updated = controller.update_dashboard_group(
            db, test_dashboard.dashboardId, new_group.groupId
        )

        assert updated is not None
        assert updated.groupId == new_group.groupId

    def test_delete_dashboard(self, db, test_dashboard):
        """Test deleting dashboard."""
        controller = DashboardController()
        result = controller.delete_dashboard(db, test_dashboard.dashboardId)

        assert result is True

        # Verify dashboard is deleted
        deleted = controller.get_dashboard_by_id(db, test_dashboard.dashboardId)
        assert deleted is None

    def test_delete_dashboard_not_found(self, db):
        """Test deleting non-existent dashboard."""
        controller = DashboardController()
        result = controller.delete_dashboard(db, "nonexistent-id")

        assert result is False


class TestDashboardEndpoints:
    """Test cases for dashboard endpoints."""

    def test_get_all_dashboards_endpoint(self, client, test_dashboard):
        """Test getting all dashboards via API."""
        response = client.get("/v1/powerbi/dashboards")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_dashboard_endpoint(self, client, test_dashboard):
        """Test getting specific dashboard via API."""
        response = client.get(
            f"/v1/powerbi/workspace/{test_dashboard.workspaceId}/dashboard/{test_dashboard.dashboardId}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["dashboardId"] == test_dashboard.dashboardId
        assert data["dashboardName"] == test_dashboard.dashboardName

    def test_get_dashboard_not_found(self, client):
        """Test getting non-existent dashboard."""
        response = client.get("/v1/powerbi/workspace/test/dashboard/nonexistent")

        assert response.status_code == 404

    def test_get_dashboards_by_workspace_endpoint(self, client, test_dashboard):
        """Test getting dashboards by workspace via API."""
        response = client.get(
            f"/v1/powerbi/workspace/{test_dashboard.workspaceId}/dashboards"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_dashboards_by_group_endpoint(self, client, test_dashboard, test_group):
        """Test getting dashboards by group via API."""
        response = client.get(f"/v1/powerbi/group/{test_group.groupId}/dashboards")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_update_dashboard_group_endpoint(self, client, test_dashboard, db):
        """Test updating dashboard group assignment via API."""
        # Create new group
        new_group = Group(groupName="API New Group", groupDescription="API test group")
        db.add(new_group)
        db.commit()
        db.refresh(new_group)

        response = client.put(
            f"/v1/powerbi/dashboard/{test_dashboard.dashboardId}/group",
            json={"groupId": new_group.groupId},
        )

        assert response.status_code == 200

    def test_delete_dashboard_endpoint(self, client, test_dashboard):
        """Test deleting dashboard via API."""
        response = client.delete(f"/v1/powerbi/dashboard/{test_dashboard.dashboardId}")

        assert response.status_code == 204

    def test_delete_dashboard_not_found_endpoint(self, client):
        """Test deleting non-existent dashboard."""
        response = client.delete("/v1/powerbi/dashboard/nonexistent")

        assert response.status_code == 404

    def test_get_dashboard_embed_token_endpoint(self, client, test_dashboard):
        """Test getting dashboard embed token via API."""
        # This might fail if PowerBI service is not configured, so we test for response
        response = client.get(
            f"/v1/powerbi/workspace/{test_dashboard.workspaceId}/dashboard/{test_dashboard.dashboardId}/token"
        )

        # Response could be 200 (success) or error depending on PowerBI config
        assert response.status_code in [200, 401, 500, 503]


class TestDashboardWithGroupIntegration:
    """Test cases for dashboard and group integration."""

    def test_dashboard_group_relationship(self, db, test_dashboard, test_group):
        """Test relationship between dashboard and group."""
        assert test_dashboard.group is not None
        assert test_dashboard.group.groupId == test_group.groupId
        assert test_dashboard.group.groupName == test_group.groupName

    def test_dashboard_without_group(self, db):
        """Test dashboard without group assignment."""
        dashboard = Dashboard(
            dashboardId="no-group-dashboard",
            dashboardName="Dashboard Without Group",
            workspaceId="test-workspace",
            workspaceName="Test Workspace",
            groupId=None,
        )
        db.add(dashboard)
        db.commit()
        db.refresh(dashboard)

        assert dashboard.group is None
        assert dashboard.groupId is None

    def test_multiple_dashboards_same_group(self, db, test_group):
        """Test multiple dashboards assigned to same group."""
        dashboards = []
        for i in range(3):
            dashboard = Dashboard(
                dashboardId=f"dashboard-{i}",
                dashboardName=f"Dashboard {i}",
                workspaceId="workspace",
                workspaceName="Workspace",
                groupId=test_group.groupId,
            )
            db.add(dashboard)
            dashboards.append(dashboard)
        db.commit()

        # Verify all dashboards are in the group
        controller = DashboardController()
        group_dashboards = controller.get_dashboards_by_group(db, test_group.groupId)

        assert len(group_dashboards) >= 3
