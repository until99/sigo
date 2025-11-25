from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from controller.auth_controller import AuthController
from schemas.user_schema import LoginRequest, LoginResponse
from database import get_db

router_auth = APIRouter()


@router_auth.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate user and generate JWT Token",
    description="Authenticate a user with email and password, returns JWT token",
    status_code=status.HTTP_200_OK,
)
def login(login_data: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """View endpoint for user login.

    Args:
        login_data: Login credentials (email and password)
        db: Database session dependency

    Returns:
        LoginResponse with access token and user data

    Raises:
        HTTPException: If credentials are invalid
    """
    result = AuthController.login(
        db=db,
        email=login_data.email,
        password=login_data.password,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return LoginResponse(**result)
