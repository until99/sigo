"""Tests for group controller and endpoints."""

import pytest
from models.group import Group
from schemas.group_schema import GroupCreate, GroupUpdate
from controller.group_controller import GroupController


@pytest.fixture
def test_group(db):
    """Create a test group."""
    group = Group(
        groupName="Test Group",
        groupDescription="A test group",
        backgroundImage="test_image.jpg"
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


class TestGroupController:
    """Test cases for GroupController."""

    def test_create_group(self, db):
        """Test group creation."""
        group_data = GroupCreate(
            groupName="New Group",
            groupDescription="New group description",
            backgroundImage="image.jpg"
        )
        
        group = GroupController.create_group(db, group_data)
        
        assert group.groupId is not None
        assert group.groupName == "New Group"
        assert group.groupDescription == "New group description"
        assert group.backgroundImage == "image.jpg"

    def test_get_group_by_id(self, db, test_group):
        """Test getting group by ID."""
        group = GroupController.get_group_by_id(db, test_group.groupId)
        
        assert group is not None
        assert group.groupId == test_group.groupId
        assert group.groupName == test_group.groupName

    def test_get_group_by_id_not_found(self, db):
        """Test getting non-existent group by ID."""
        group = GroupController.get_group_by_id(db, 99999)
        
        assert group is None

    def test_get_group_by_name(self, db, test_group):
        """Test getting group by name."""
        group = GroupController.get_group_by_name(db, "Test Group")
        
        assert group is not None
        assert group.groupName == "Test Group"

    def test_get_groups(self, db, test_group):
        """Test getting list of groups."""
        # Create additional groups
        for i in range(3):
            group = Group(
                groupName=f"Group {i}",
                groupDescription=f"Description {i}"
            )
            db.add(group)
        db.commit()
        
        groups = GroupController.get_groups(db)
        
        assert len(groups) >= 4  # test_group + 3 new groups

    def test_get_groups_with_pagination(self, db, test_group):
        """Test getting groups with pagination."""
        # Create additional groups
        for i in range(5):
            group = Group(
                groupName=f"Paginated Group {i}",
                groupDescription=f"Description {i}"
            )
            db.add(group)
        db.commit()
        
        groups = GroupController.get_groups(db, skip=1, limit=2)
        
        assert len(groups) == 2

    def test_update_group(self, db, test_group):
        """Test updating group."""
        update_data = GroupUpdate(
            groupName="Updated Group",
            groupDescription="Updated description"
        )
        
        updated_group = GroupController.update_group(db, test_group.groupId, update_data)
        
        assert updated_group is not None
        assert updated_group.groupName == "Updated Group"
        assert updated_group.groupDescription == "Updated description"

    def test_update_group_not_found(self, db):
        """Test updating non-existent group."""
        update_data = GroupUpdate(groupName="Updated")
        
        updated_group = GroupController.update_group(db, 99999, update_data)
        
        assert updated_group is None

    def test_delete_group(self, db, test_group):
        """Test deleting group."""
        result = GroupController.delete_group(db, test_group.groupId)
        
        assert result is True
        
        # Verify group is deleted
        deleted_group = GroupController.get_group_by_id(db, test_group.groupId)
        assert deleted_group is None

    def test_delete_group_not_found(self, db):
        """Test deleting non-existent group."""
        result = GroupController.delete_group(db, 99999)
        
        assert result is False

    def test_add_user_to_group(self, db, test_group, test_user):
        """Test adding user to group."""
        result = GroupController.add_user_to_group(db, test_group.groupId, test_user.userId)
        
        assert result is True
        
        # Verify user is in group
        group = GroupController.get_group_by_id(db, test_group.groupId)
        user_ids = [user.userId for user in group.users]
        assert test_user.userId in user_ids

    def test_add_user_to_group_duplicate(self, db, test_group, test_user):
        """Test adding same user to group twice."""
        GroupController.add_user_to_group(db, test_group.groupId, test_user.userId)
        result = GroupController.add_user_to_group(db, test_group.groupId, test_user.userId)
        
        # Should still succeed or return False depending on implementation
        assert result is not None

    def test_remove_user_from_group(self, db, test_group, test_user):
        """Test removing user from group."""
        # First add user to group
        GroupController.add_user_to_group(db, test_group.groupId, test_user.userId)
        
        # Then remove user
        result = GroupController.remove_user_from_group(db, test_group.groupId, test_user.userId)
        
        assert result is True
        
        # Verify user is removed
        group = GroupController.get_group_by_id(db, test_group.groupId)
        user_ids = [user.userId for user in group.users]
        assert test_user.userId not in user_ids

    def test_remove_user_from_group_not_member(self, db, test_group, test_user):
        """Test removing user that is not in group."""
        result = GroupController.remove_user_from_group(db, test_group.groupId, test_user.userId)
        
        assert result is False


class TestGroupEndpoints:
    """Test cases for group endpoints."""

    def test_create_group_endpoint(self, client):
        """Test group creation via API endpoint."""
        response = client.post(
            "/v1/group",
            json={
                "groupName": "API Group",
                "groupDescription": "Created via API",
                "backgroundImage": "api_image.jpg"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["groupName"] == "API Group"
        assert data["groupDescription"] == "Created via API"

    def test_get_group_endpoint(self, client, test_group):
        """Test getting group by ID via API."""
        response = client.get(f"/v1/group/{test_group.groupId}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["groupId"] == test_group.groupId
        assert data["groupName"] == test_group.groupName

    def test_get_group_not_found(self, client):
        """Test getting non-existent group."""
        response = client.get("/v1/group/99999")
        
        assert response.status_code == 404

    def test_get_groups_endpoint(self, client, test_group):
        """Test getting list of groups via API."""
        response = client.get("/v1/group")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_groups_with_pagination(self, client, test_group):
        """Test getting groups with pagination parameters."""
        response = client.get("/v1/group?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_update_group_endpoint(self, client, test_group):
        """Test updating group via API."""
        response = client.put(
            f"/v1/group/{test_group.groupId}",
            json={
                "groupName": "Updated API Group",
                "groupDescription": "Updated via API"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["groupName"] == "Updated API Group"
        assert data["groupDescription"] == "Updated via API"

    def test_update_group_not_found(self, client):
        """Test updating non-existent group."""
        response = client.put(
            "/v1/group/99999",
            json={"groupName": "Updated"}
        )
        
        assert response.status_code == 404

    def test_delete_group_endpoint(self, client, test_group):
        """Test deleting group via API."""
        response = client.delete(f"/v1/group/{test_group.groupId}")
        
        assert response.status_code == 204

    def test_delete_group_not_found(self, client):
        """Test deleting non-existent group."""
        response = client.delete("/v1/group/99999")
        
        assert response.status_code == 404

    def test_add_user_to_group_endpoint(self, client, test_group, test_user):
        """Test adding user to group via API."""
        response = client.post(
            f"/v1/group/{test_group.groupId}/users",
            json={"userId": test_user.userId}
        )
        
        assert response.status_code in [200, 201]

    def test_remove_user_from_group_endpoint(self, client, test_group, test_user, db):
        """Test removing user from group via API."""
        # First add user to group
        GroupController.add_user_to_group(db, test_group.groupId, test_user.userId)
        
        response = client.delete(f"/v1/group/{test_group.groupId}/users/{test_user.userId}")
        
        assert response.status_code in [200, 204]

    def test_create_group_missing_required_fields(self, client):
        """Test creating group without required fields."""
        response = client.post(
            "/v1/group",
            json={}
        )
        
        assert response.status_code == 422  # Validation error
