"""OAuth2 authentication and security configuration."""

from litestar.connection import ASGIConnection
from litestar.security.jwt import OAuth2PasswordBearerAuth, Token

from app.config import settings
from app.models import User
from app.repositories.user import UserRepository


async def retrieve_user_handler(token: Token, _: ASGIConnection) -> User | None:
    """Retrieve user based on JWT token."""
    from app.db import sqlalchemy_config

    with sqlalchemy_config.get_session() as session:
        users_repo = UserRepository(session=session)

        try:
            return users_repo.get_one(username=token.sub)
        except Exception:
            return None


oauth2_auth = OAuth2PasswordBearerAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=settings.jwt_secret,
    token_url="/auth/login",
    exclude=["/auth/login", "/schema"],
)
