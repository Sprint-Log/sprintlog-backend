"""This is the top-level of the application and should only ever import from
other sub-packages of the application, and never be imported from. I.e., never
do `from app.main import whatever` from within any other module of any other
sub-package of the application.

The main point of this restriction is to support unit-testing. We need to ensure that we can load
any other component of the application for mocking things out in the unittests, without this module
being loaded before that mocking has been completed.

When writing tests, always use the `app` fixture, never import the app directly from this module.
"""
import uvicorn
from pydantic import SecretStr
from starlite import Provide, Starlite
from starlite.middleware.session.memory_backend import MemoryBackendConfig
from starlite.plugins.sql_alchemy import SQLAlchemyPlugin
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

from app import worker
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
from app.lib.dependencies import create_collection_dependencies, provide_user
from app.lib.health import health_check
from app.lib.redis import redis
from app.lib.repository.exceptions import RepositoryException
from app.lib.service import ServiceException
from app.lib.type_encoders import type_encoders_map
from app.lib.worker import create_worker_instance

from .controllers import tasks

dependencies = {
    settings.api.USER_DEPENDENCY_KEY: Provide(provide_user),
}
dependencies.update(create_collection_dependencies())
worker_instance = create_worker_instance(worker.functions)
starlite_users = StarliteUsers(
    config=StarliteUsersConfig(
        auth_backend="jwt",
        secret=SecretStr("sixteenbits"),
        session_backend_config=MemoryBackendConfig(),
        user_model=User,
        user_read_dto=UserReadDTO,
        user_create_dto=UserCreateDTO,
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
        role_management_handler_config=RoleManagementHandlerConfig(
            guards=[roles_accepted("administrator")]
        ),
        user_management_handler_config=UserManagementHandlerConfig(
            guards=[roles_required("administrator")]
        ),
        verification_handler_config=VerificationHandlerConfig(),
    )
)

app = Starlite(
    after_exception=[exceptions.after_exception_hook_handler],
    cache_config=cache.config,
    compression_config=compression.config,
    dependencies=dependencies,
    exception_handlers={
        RepositoryException: exceptions.repository_exception_to_http_response,
        ServiceException: exceptions.service_exception_to_http_response,
    },
    logging_config=logging.config,
    openapi_config=openapi.config,
    route_handlers=[health_check, tasks.ApiController],
    plugins=[SQLAlchemyPlugin(config=sqlalchemy_plugin.config)],
    on_app_init=[starlite_users.on_app_init],
    on_shutdown=[worker_instance.stop, redis.close],
    on_startup=[worker_instance.on_app_startup, sentry.configure],
    static_files_config=static_files.config,
    type_encoders=type_encoders_map,
)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.server.HOST,
        log_level=settings.server.LOG_LEVEL,
        port=settings.server.PORT,
        reload=settings.server.RELOAD,
        timeout_keep_alive=settings.server.KEEPALIVE,
    )
