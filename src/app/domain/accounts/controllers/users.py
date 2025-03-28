"""User Account Controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from litestar import Controller, delete, get, patch, post, Response
from litestar.di import Provide
from litestar.params import Dependency, Parameter
from litestar.exceptions import NotFoundException, NotAuthorizedException, PermissionDeniedException

from app.domain.accounts import urls
from app.domain.accounts.deps import provide_users_service
from app.domain.accounts.guards import requires_superuser, requires_active_user
from app.domain.accounts.schemas import User, UserCreate, UserUpdate, UserUpdatePassword
from app.lib.deps import create_filter_dependencies
from app.lib.crypt import get_password_hash
from app.db.models.enums import PaymentMethod
from structlog import get_logger
from app.db import models as m

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes
    from advanced_alchemy.service import OffsetPagination
    from app.domain.accounts.services import UserService

logger = get_logger()


class UserController(Controller):
    """User Account Controller."""

    tags = ["User Accounts"]
    dependencies = {
        "users_service": Provide(provide_users_service),
    } | create_filter_dependencies(
        {
            "id_filter": UUID,
            "search": "name,email",
            "pagination_type": "limit_offset",
            "pagination_size": 20,
            "created_at": True,
            "updated_at": True,
            "sort_field": "name",
            "sort_order": "asc",
        },
    )

    @get(operation_id="ListUsers", path=urls.ACCOUNT_LIST, guards=[requires_superuser])
    async def list_users(
        self,
        users_service: UserService,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> OffsetPagination[User]:
        """List users."""
        results, total = await users_service.list_and_count(*filters)
        return users_service.to_schema(data=results, total=total, schema_type=User, filters=filters)

    @get(operation_id="GetUser", path=urls.ACCOUNT_DETAIL, guards=[requires_superuser])
    async def get_user(
        self,
        users_service: UserService,
        user_id: Annotated[UUID, Parameter(title="User ID", description="The user to retrieve.")],
    ) -> User:
        """Get a user."""
        db_obj = await users_service.get(user_id)
        return users_service.to_schema(db_obj, schema_type=User)

    @post(operation_id="CreateUser", path=urls.ACCOUNT_CREATE, guards=[requires_superuser])
    async def create_user(self, users_service: UserService, data: UserCreate) -> User:
        """Create a new user with optional bank accounts."""
        user_data = data.to_dict()
        bank_accounts_data = user_data.pop("bank_accounts", [])

        user = await users_service.create(user_data, auto_commit=True)
        if len(bank_accounts_data) > 0:
            bank_account_objs = [
                m.BankAccount(method=PaymentMethod(account.method), account_number=account.account_number)
                for account in bank_accounts_data
            ]

            user.bank_accounts = bank_account_objs

        return users_service.to_schema(user, schema_type=User)

    @patch(
        operation_id="UpdateUser",
        path=urls.ACCOUNT_UPDATE,
        guards=[requires_active_user],
    )
    async def update_user(
        self,
        data: UserUpdate,
        users_service: UserService,
        user_id: UUID = Parameter(title="User ID", description="The user to update."),
    ) -> User:
        """Update user data."""

        user = await users_service.authenticate(username=data.email, password=data.password)
        if not user:
            raise NotAuthorizedException("Invalid credentials!")

        if user_id != user.id and not user.is_superuser:
            raise PermissionDeniedException("Only allow superuser to proceed this action!")

        update_data = {}

        if "email" in data.to_dict():
            update_data["email"] = data.email

        if "name" in data.to_dict():
            update_data["name"] = data.name

        if "avatar_url" in data.to_dict():
            update_data["avatar_url"] = data.avatar_url

        if "is_superuser" in data.to_dict() and user.is_superuser:
            update_data["is_superuser"] = data.is_superuser

        db_obj = await users_service.update(item_id=user_id, data=update_data)

        return users_service.to_schema(db_obj, schema_type=User)

    @patch(
        operation_id="UpdateUserPassword",
        path=urls.ACCOUNT_UPDATE_PASSWORD,
        guards=[requires_active_user],
    )
    async def update_user_password(
        self,
        data: UserUpdatePassword,
        users_service: UserService,
        current_user: m.User,
        user_id: UUID = Parameter(title="User ID", description="The user to update."),
    ) -> Response:
        """Update a user's password."""
        # If the current user is not a superuser, verify the provided old password.
        if data.new_password != data.confirm_password:
            return Response(content="Confirm password and new password are not matched!", status_code=409)

        if not current_user.is_superuser:
            user_obj = await users_service.authenticate(username=current_user.email, password=data.old_password)

            current_password = data.old_password
        else:
            # If superuser, get the target user by id.
            user_obj = await users_service.get_one_or_none(item_id=user_id)
            if user_obj is None:
                raise NotFoundException("User not found!")
            current_password = user_obj.hashed_password

        # Prevent non-superuser from updating other users’ passwords.
        if user_id != current_user.id and not current_user.is_superuser:
            raise PermissionDeniedException("Only allow superuser to proceed this action!")

        hashed_password = get_password_hash(data.new_password)
        paswd_data = {"hashed_password": hashed_password, "current_password": current_password}

        await users_service.update_password(data=paswd_data, db_obj=user_obj)
        return Response(
            content="Password is successfully updated!",
            status_code=200,
        )

    @delete(operation_id="DeactivateUser", path=urls.ACCOUNT_DELETE, guards=[requires_superuser])
    async def deactivate_user(
        self,
        users_service: UserService,
        user_id: Annotated[UUID, Parameter(title="User ID", description="The user to delete.")],
    ) -> None:
        """Delete a user from the system."""
        user_obj = await users_service.update(item_id=user_id, data={"is_active": False})
        _ = users_service.to_schema(user_obj, schema_type=User)
