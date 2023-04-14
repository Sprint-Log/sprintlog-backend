from typing import Any
from uuid import UUID

import uvicorn
from litestar import Litestar
from litestar.contrib.repository.abc import FilterTypes
from litestar.contrib.repository.exceptions import RepositoryError as RepositoryException
from litestar.contrib.repository.filters import (
    BeforeAfter,
    CollectionFilter,
    LimitOffset,
)
from litestar.stores.registry import StoreRegistry
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlite_users import StarliteUsers, StarliteUsersConfig
from starlite_users.config import (
    AuthHandlerConfig,
    CurrentUserHandlerConfig,
    PasswordResetHandlerConfig,
    RegisterHandlerConfig,
    RoleManagementHandlerConfig,
    UserManagementHandlerConfig,
    VerificationHandlerConfig,
)
from starlite_users.guards import roles_accepted, roles_required

from app.controllers import create_router
from app.domain.users import (
    Role,
    RoleCreateDTO,
    RoleReadDTO,
    RoleUpdateDTO,
    User,
    UserCreateDTO,
    UserReadDTO,
    UserService,
    UserUpdateDTO,
)
from app.lib import (
    cache,
    compression,
    exceptions,
    logging,
    openapi,
    sentry,
    settings,
    sqlalchemy_plugin,
    static_files,
)
from app.lib.dependencies import create_collection_dependencies
from app.lib.health import health_check
from app.lib.redis import redis
from app.lib.service import ServiceError
from app.lib.type_encoders import type_encoders_map

__all__ = ["create_app"]


dependencies = create_collection_dependencies()
su = StarliteUsers(
    config=StarliteUsersConfig(
        auth_backend="jwt",
        secret=SecretStr("1234567890123456"),
        # session_backend_config=MemoryBackendConfig(),
        user_model=User,
        user_create_dto=UserCreateDTO,
        user_read_dto=UserReadDTO,
        user_update_dto=UserUpdateDTO,
        role_model=Role,
        role_create_dto=RoleCreateDTO,
        role_read_dto=RoleReadDTO,
        role_update_dto=RoleUpdateDTO,
        user_service_class=UserService,  # pyright: ignore
        auth_handler_config=AuthHandlerConfig(),
        current_user_handler_config=CurrentUserHandlerConfig(),
        password_reset_handler_config=PasswordResetHandlerConfig(),
        register_handler_config=RegisterHandlerConfig(),
        role_management_handler_config=RoleManagementHandlerConfig(guards=[roles_accepted("administrator")]),
        user_management_handler_config=UserManagementHandlerConfig(guards=[roles_required("administrator")]),
        verification_handler_config=VerificationHandlerConfig(),
    )
)


def create_app(**kwargs: Any) -> Litestar:

    kwargs.setdefault("debug", settings.app.DEBUG)
    return Litestar(
        on_app_init=[su.on_app_init],
        response_cache_config=cache.config,
        stores=StoreRegistry(default_factory=cache.redis_store_factory),
        compression_config=compression.config,
        dependencies=dependencies,
        exception_handlers={
            RepositoryException: exceptions.repository_exception_to_http_response,
            ServiceError: exceptions.service_exception_to_http_response,
        },
        logging_config=logging.config,
        openapi_config=openapi.config,
        route_handlers=[health_check, create_router()],
        on_shutdown=[redis.close],
        on_startup=[sentry.configure],
        plugins=[sqlalchemy_plugin.plugin],
        preferred_validation_backend="pydantic",
        signature_namespace={
            "AsyncSession": AsyncSession,
            "FilterTypes": FilterTypes,
            "BeforeAfter": BeforeAfter,
            "CollectionFilter": CollectionFilter,
            "LimitOffset": LimitOffset,
            "UUID": UUID,
        },
        static_files_config=[static_files.config],
        type_encoders=type_encoders_map,
        **kwargs,
    )


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.server.HOST,
        log_level=settings.server.LOG_LEVEL,
        port=settings.server.PORT,
        reload=settings.server.RELOAD,
        timeout_keep_alive=settings.server.KEEPALIVE,
    )
