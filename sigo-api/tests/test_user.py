"""Tests for user controller and endpoints."""

import pytest
from models.user import User
from schemas.user_schema import UserCreate, UserUpdate
from controller.user_controller import UserController


class TestUserController:
    """Test cases for UserController."""

    def test_create_user(self, db):
        """Test user creation."""
        user_data = UserCreate(
            username="newuser",
            email="newuser@example.com",
            password="password123",
            userBusinessArea="Sales",
            isActive=True
        )
        
        user = UserController.create_user(db, user_data)
        
        assert user.userId is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.userBusinessArea == "Sales"
        assert user.isActive is True
        assert user.hashedPassword != "password123"  # Password should be hashed

    def test_get_user_by_id(self, db, test_user):
        """Test getting user by ID."""
        user = UserController.get_user_by_id(db, test_user.userId)
        
        assert user is not None
        assert user.userId == test_user.userId
        assert user.email == test_user.email

    def test_get_user_by_id_not_found(self, db):
        """Test getting non-existent user by ID."""
        user = UserController.get_user_by_id(db, 99999)
        
        assert user is None

    def test_get_user_by_email(self, db, test_user):
        """Test getting user by email."""
        user = UserController.get_user_by_email(db, "test@example.com")
        
        assert user is not None
        assert user.email == "test@example.com"

    def test_get_user_by_email_not_found(self, db):
        """Test getting non-existent user by email."""
        user = UserController.get_user_by_email(db, "nonexistent@example.com")
        
        assert user is None

    def test_get_users(self, db, test_user):
        """Test getting list of users."""
        # Create additional users
        for i in range(3):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                hashedPassword=User.hash_password("password"),
                userBusinessArea="Test",
                isActive=True
            )
            db.add(user)
        db.commit()
        
        users = UserController.get_users(db)
        
        assert len(users) >= 4  # test_user + 3 new users
        
    def test_get_users_with_pagination(self, db, test_user):
        """Test getting users with pagination."""
        # Create additional users
        for i in range(5):
            user = User(
                username=f"paginateduser{i}",
                email=f"paginateduser{i}@example.com",
                hashedPassword=User.hash_password("password"),
                userBusinessArea="Test",
                isActive=True
            )
            db.add(user)
        db.commit()
        
        users = UserController.get_users(db, skip=1, limit=2)
        
        assert len(users) == 2

    def test_update_user(self, db, test_user):
        """Test updating user."""
        update_data = UserUpdate(
            username="updateduser",
            userBusinessArea="Marketing"
        )
        
        updated_user = UserController.update_user(db, test_user.userId, update_data)
        
        assert updated_user is not None
        assert updated_user.username == "updateduser"
        assert updated_user.userBusinessArea == "Marketing"
        assert updated_user.email == test_user.email  # Email unchanged

    def test_update_user_not_found(self, db):
        """Test updating non-existent user."""
        update_data = UserUpdate(username="updated")
        
        updated_user = UserController.update_user(db, 99999, update_data)
        
        assert updated_user is None

    def test_delete_user(self, db, test_user):
        """Test deleting user."""
        result = UserController.delete_user(db, test_user.userId)
        
        assert result is True
        
        # Verify user is deleted
        deleted_user = UserController.get_user_by_id(db, test_user.userId)
        assert deleted_user is None

    def test_delete_user_not_found(self, db):
        """Test deleting non-existent user."""
        result = UserController.delete_user(db, 99999)
        
        assert result is False


class TestUserEndpoints:
    """Test cases for user endpoints."""

    def test_create_user_endpoint(self, client):
        """Test user creation via API endpoint."""
        response = client.post(
            "/v1/users",
            json={
                "username": "apiuser",
                "email": "apiuser@example.com",
                "password": "password123",
                "userBusinessArea": "IT",
                "isActive": True
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "apiuser"
        assert data["email"] == "apiuser@example.com"
        assert "hashedPassword" not in data  # Password should not be in response

    def test_create_user_duplicate_email(self, client, test_user):
        """Test creating user with duplicate email."""
        response = client.post(
            "/v1/users",
            json={
                "username": "duplicate",
                "email": "test@example.com",  # Already exists
                "password": "password123",
                "userBusinessArea": "IT",
                "isActive": True
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_get_user_endpoint(self, client, test_user):
        """Test getting user by ID via API."""
        response = client.get(f"/v1/users/{test_user.userId}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["userId"] == test_user.userId
        assert data["email"] == test_user.email

    def test_get_user_not_found(self, client):
        """Test getting non-existent user."""
        response = client.get("/v1/users/99999")
        
        assert response.status_code == 404

    def test_get_users_endpoint(self, client, test_user):
        """Test getting list of users via API."""
        response = client.get("/v1/users")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_users_with_pagination(self, client, test_user):
        """Test getting users with pagination parameters."""
        response = client.get("/v1/users?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_update_user_endpoint(self, client, test_user):
        """Test updating user via API."""
        response = client.put(
            f"/v1/users/{test_user.userId}",
            json={
                "username": "updated_username",
                "userBusinessArea": "Updated Area"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "updated_username"
        assert data["userBusinessArea"] == "Updated Area"

    def test_update_user_not_found(self, client):
        """Test updating non-existent user."""
        response = client.put(
            "/v1/users/99999",
            json={"username": "updated"}
        )
        
        assert response.status_code == 404

    def test_delete_user_endpoint(self, client, test_user):
        """Test deleting user via API."""
        response = client.delete(f"/v1/users/{test_user.userId}")
        
        assert response.status_code == 204

    def test_delete_user_not_found(self, client):
        """Test deleting non-existent user."""
        response = client.delete("/v1/users/99999")
        
        assert response.status_code == 404

    def test_create_user_invalid_email(self, client):
        """Test creating user with invalid email format."""
        response = client.post(
            "/v1/users",
            json={
                "username": "testuser",
                "email": "invalid-email",
                "password": "password123",
                "userBusinessArea": "IT",
                "isActive": True
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_create_user_missing_required_fields(self, client):
        """Test creating user without required fields."""
        response = client.post(
            "/v1/users",
            json={"username": "testuser"}
        )
        
        assert response.status_code == 422  # Validation error
