"""User Account Controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from litestar import Controller, delete, get, patch, post, Response
from litestar.di import Provide
from litestar.params import Dependency, Parameter
from litestar.exceptions import NotFoundException, NotAuthorizedException, PermissionDeniedException

from app.domain.accounts import urls
from app.domain.accounts.deps import provide_user_service
from app.domain.accounts.guards import requires_superuser, requires_active_user
from app.domain.accounts.schemas import User, UserCreate, UserUpdate, UserUpdatePassword
from app.lib.deps import create_filter_dependencies
from app.db.models.enums import PaymentMethod
from structlog import get_logger
from app.db import models as m
from advanced_alchemy.filters import OrderBy


if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes
    from advanced_alchemy.service import OffsetPagination
    from app.domain.accounts.services import UserService

logger = get_logger()


class UserController(Controller):
    """User Account Controller."""

    tags = ["User Accounts"]
    dependencies = {
        "user_service": Provide(provide_user_service),
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
        user_service: UserService,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> OffsetPagination[User]:
        """List users."""
        default_filters = [
            OrderBy(field_name="is_active", sort_order="desc"),
            OrderBy(field_name="created_at", sort_order="desc"),
        ] + (filters or [])
        results, total = await user_service.list_and_count(*default_filters)
        return user_service.to_schema(data=results, total=total, schema_type=User, filters=filters)

    @get(operation_id="GetUser", path=urls.ACCOUNT_DETAIL, guards=[requires_superuser])
    async def get_user(
        self,
        user_service: UserService,
        user_id: Annotated[UUID, Parameter(title="User ID", description="The user to retrieve.")],
    ) -> User:
        """Get a user."""
        db_obj = await user_service.get(user_id)
        return user_service.to_schema(db_obj, schema_type=User)

    @post(operation_id="CreateUser", path=urls.ACCOUNT_CREATE, guards=[requires_superuser])
    async def create_user(self, user_service: UserService, data: UserCreate) -> User:
        """Create a new user with optional bank accounts."""
        user_data = data.to_dict()
        user_data["is_active"] = True
        user_data["is_verified"] = False

        bank_accounts_data = user_data.pop("bank_accounts", [])

        user = await user_service.create(user_data, auto_commit=True)
        if len(bank_accounts_data) > 0:
            bank_account_objs = [
                m.BankAccount(method=PaymentMethod(account.method), account_number=account.account_number)
                for account in bank_accounts_data
            ]

            user.bank_accounts = bank_account_objs

        return user_service.to_schema(user, schema_type=User)

    @patch(
        operation_id="UpdateUser",
        path=urls.ACCOUNT_UPDATE,
        guards=[requires_active_user],
    )
    async def update_user(
        self,
        data: UserUpdate,
        user_service: UserService,
        current_user: m.User,
        user_id: UUID = Parameter(title="User ID", description="The user to update."),
    ) -> User:
        """Update user data."""

        user = await user_service.authenticate(username=current_user.email, password=data.password)
        if not user:
            raise NotAuthorizedException("Invalid credentials!")

        if user_id != user.id and not user.is_superuser:
            raise PermissionDeniedException("Only allow superuser to proceed this action!")

        update_data = data.to_dict()
        if "password" in update_data:
            del update_data["password"]
        if "hashed_password" in update_data:
            del update_data["hashed_password"]

        if "is_superuser" in update_data and not user.is_superuser:
            raise PermissionDeniedException("Only allow superuser to proceed this action!")

        db_obj = await user_service.update(item_id=user_id, data=update_data)

        if "bank_accounts" in update_data:
            bank_accounts_data = update_data["bank_accounts"]
            bank_account_objs = [
                m.BankAccount(method=PaymentMethod(account.method), account_number=account.account_number)
                for account in bank_accounts_data
            ]

            db_obj.bank_accounts = bank_account_objs

        return user_service.to_schema(db_obj, schema_type=User)

    @patch(
        operation_id="UpdateUserPassword",
        path=urls.ACCOUNT_UPDATE_PASSWORD,
        guards=[requires_active_user],
    )
    async def update_user_password(
        self,
        data: UserUpdatePassword,
        user_service: UserService,
        current_user: m.User,
        user_id: UUID = Parameter(title="User ID", description="The user to update."),
    ) -> Response:
        """Update a user's password."""
        user_obj = await user_service.get_one_or_none(id=user_id)
        if user_obj is None:
            raise NotFoundException("User not found!")

        if current_user.id != user_id and not current_user.is_superuser:
            raise PermissionDeniedException("Only allow superuser to proceed this action!")

        await user_service.authenticate(username=user_obj.email, password=data.current_password)

        await user_service.update_password(data=data.to_dict(), db_obj=user_obj)
        return Response(
            content="Password is successfully updated!",
            status_code=200,
        )

    @delete(operation_id="DeactivateUser", path=urls.ACCOUNT_DELETE, guards=[requires_superuser])
    async def deactivate_user(
        self,
        user_service: UserService,
        user_id: Annotated[UUID, Parameter(title="User ID", description="The user to delete.")],
    ) -> None:
        """Delete a user from the system."""
        user_obj = await user_service.update(item_id=user_id, data={"is_active": False})
        _ = user_service.to_schema(user_obj, schema_type=User)
