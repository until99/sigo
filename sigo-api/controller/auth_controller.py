from models.auth import Login


class AuthController:
    @classmethod
    async def login(cls, user: Login) -> Login:
        return user
