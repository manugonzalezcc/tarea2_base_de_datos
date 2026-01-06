"""Controller for authentication endpoints."""

from typing import Annotated

from litestar import Controller, Response, post
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.security.jwt import OAuth2Login

from app.repositories.user import UserRepository, password_hasher, provide_user_repo
from app.security import oauth2_auth


class AuthController(Controller):
    """Controller for authentication operations."""

    path = "/auth"
    tags = ["auth"]

    @post(
        "/login",
        dependencies={"users_repo": Provide(provide_user_repo)},
    )
    async def login(
        self,
        data: Annotated[dict[str, str], Body(media_type=RequestEncodingType.URL_ENCODED)],
        users_repo: UserRepository,
    ) -> Response[OAuth2Login]:
        """Authenticate user and generate OAuth2 token."""
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise HTTPException(status_code=400, detail="username y password son requeridos")

        user = users_repo.get_one_or_none(username=username)

        if user is not None:
            if password_hasher.verify(password, user.password):
                return oauth2_auth.login(identifier=user.username)

        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
