"""User Account Controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from litestar import Controller, Request, Response, get, post
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body

from app.domain.accounts import urls
from app.domain.accounts.deps import provide_user_service
from app.domain.accounts.guards import auth, requires_active_user
from app.domain.accounts.schemas import AccountLogin, AccountRegister, User
from structlog import get_logger
from litestar.response import Redirect

if TYPE_CHECKING:
    from litestar.security.jwt import OAuth2Login

    from app.db import models as m
    from app.domain.accounts.services import UserService

logger = get_logger()


class AccessController(Controller):
    """User login and registration."""

    tags = ["Access"]
    dependencies = {
        "users_service": Provide(provide_user_service),
    }

    @post(operation_id="AccountLogin", path=urls.ACCOUNT_LOGIN, exclude_from_auth=True)
    async def login(
        self,
        users_service: UserService,
        data: Annotated[AccountLogin, Body(title="Login", media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Response[OAuth2Login]:
        """Authenticate a user."""
        user = await users_service.authenticate(data.username, data.password)
        return auth.login(str(user.id))

    @post(operation_id="AccountRegister", path=urls.ACCOUNT_REGISTER)
    async def signup(
        self,
        request: Request,
        users_service: UserService,
        data: AccountRegister,
    ) -> User:
        """User Signup."""
        user_data = data.to_dict()
        user = await users_service.create(user_data)
        request.app.emit(event_id="user_created", user_id=user.id)
        return users_service.to_schema(user, schema_type=User)

    @get(operation_id="AccountProfile", path=urls.ACCOUNT_PROFILE, guards=[requires_active_user])
    async def profile(self, current_user: m.User, users_service: UserService) -> User:
        """User Profile."""
        return users_service.to_schema(current_user, schema_type=User)

    @post(operation_id="AccountLogout", path=urls.ACCOUNT_LOGOUT, guards=[requires_active_user])
    async def logout(self) -> Redirect:
        """Logout endpoint that clears the auth token cookie and redirects to login."""
        response = Redirect(path="/login")
        response.set_cookie(key="token", value="", path="/", httponly=True, max_age=0)
        return response
