"""Tests for authentication controller and endpoints."""

import pytest
from datetime import timedelta
from jose import jwt

from controller.auth_controller import AuthController, SECRET_KEY, ALGORITHM
from models.user import User


class TestAuthController:
    """Test cases for AuthController."""

    def test_authenticate_user_success(self, db, test_user):
        """Test successful user authentication."""
        user = AuthController.authenticate_user(
            db=db, email="test@example.com", password="testpass123"
        )

        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"

    def test_authenticate_user_wrong_password(self, db, test_user):
        """Test authentication with wrong password."""
        user = AuthController.authenticate_user(
            db=db, email="test@example.com", password="wrongpassword"
        )

        assert user is None

    def test_authenticate_user_nonexistent_email(self, db):
        """Test authentication with non-existent email."""
        user = AuthController.authenticate_user(
            db=db, email="nonexistent@example.com", password="password"
        )

        assert user is None

    def test_authenticate_inactive_user(self, db):
        """Test authentication with inactive user."""
        inactive_user = User(
            username="inactive",
            email="inactive@example.com",
            hashedPassword=User.hash_password("password"),
            userBusinessArea="Test",
            isActive=False,
        )
        db.add(inactive_user)
        db.commit()

        user = AuthController.authenticate_user(
            db=db, email="inactive@example.com", password="password"
        )

        assert user is None

    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "test@example.com", "user_id": 1}
        token = AuthController.create_access_token(data)

        assert token is not None

        # Decode and verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert "exp" in payload

    def test_create_access_token_custom_expiry(self):
        """Test JWT token creation with custom expiry."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=60)
        token = AuthController.create_access_token(data, expires_delta)

        assert token is not None

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "test@example.com"

    def test_login_success(self, db, test_user):
        """Test successful login process."""
        result = AuthController.login(
            db=db, email="test@example.com", password="testpass123"
        )

        assert result is not None
        assert "access_token" in result
        assert result["token_type"] == "bearer"
        assert "user" in result
        assert result["user"].email == "test@example.com"

    def test_login_failure(self, db, test_user):
        """Test failed login process."""
        result = AuthController.login(
            db=db, email="test@example.com", password="wrongpassword"
        )

        assert result is None


class TestAuthEndpoints:
    """Test cases for authentication endpoints."""

    def test_login_endpoint_success(self, client, test_user):
        """Test successful login via API endpoint."""
        response = client.post(
            "/v1/login", json={"email": "test@example.com", "password": "testpass123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"

    def test_login_endpoint_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        response = client.post(
            "/v1/login", json={"email": "test@example.com", "password": "wrongpassword"}
        )

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_login_endpoint_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/v1/login",
            json={"email": "nonexistent@example.com", "password": "password"},
        )

        assert response.status_code == 401

    def test_login_endpoint_missing_fields(self, client):
        """Test login with missing required fields."""
        response = client.post("/v1/login", json={"email": "test@example.com"})

        assert response.status_code == 422  # Validation error

    def test_login_endpoint_invalid_email_format(self, client):
        """Test login with invalid email format."""
        response = client.post(
            "/v1/login", json={"email": "invalid-email", "password": "password"}
        )

        assert response.status_code == 422  # Validation error
