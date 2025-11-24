from fastapi import APIRouter

from controller.auth_controller import AuthController
from models.auth import Login


router_auth = APIRouter()


@router_auth.post(
    "/login",
    response_model=Login,
    summary="Authenticate user and generate JWT Token",
)
async def login(user: Login) -> Login:
    return await AuthController.login(user)
