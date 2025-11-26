"""Test fixtures and configuration for pytest."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from models.user import User
from views.auth_view import router_auth
from views.user_view import router_user
from views.group_view import router_group
from views.dashboard_view import router_dashboard

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_test_app() -> FastAPI:
    """Create FastAPI app for testing without database initialization."""
    app = FastAPI(
        title="SIGO API - Test",
        description="API for SIGO application - Test Environment",
        version="1.0.0",
    )

    app.include_router(router_auth, prefix="/v1", tags=["Authentication"])
    app.include_router(router_user, prefix="/v1", tags=["Users"])
    app.include_router(router_group, prefix="/v1", tags=["Groups"])
    app.include_router(router_dashboard, prefix="/v1", tags=["Dashboards"])

    @app.get("/", tags=["Health Check"])
    def read_root():
        """Health check endpoint."""
        return {"status": "ok", "message": "SIGO API is running"}

    return app


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override."""
    app = create_test_app()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashedPassword=User.hash_password("testpass123"),
        userBusinessArea="Testing",
        isActive=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post(
        "/v1/auth/login", json={"email": "test@example.com", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
