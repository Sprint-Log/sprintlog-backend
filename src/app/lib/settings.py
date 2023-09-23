from __future__ import annotations

import importlib
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Final, Literal

from dotenv import load_dotenv
from litestar.data_extractors import RequestExtractorField, ResponseExtractorField  # noqa: TCH002
from pydantic import ValidationError, field_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from app import utils

__all__ = [
    "DatabaseSettings",
    "AppSettings",
    "OpenAPISettings",
    "RedisSettings",
    "LogSettings",
    "WorkerSettings",
    "ServerSettings",
    "app",
    "db",
    "openapi",
    "redis",
    "server",
    "log",
    "worker",
]

DEFAULT_MODULE_NAME = "app"
BASE_DIR: Final = utils.module_to_os_path(DEFAULT_MODULE_NAME)
STATIC_DIR = Path(BASE_DIR / "domain" / "web" / "public")
TEMPLATES_DIR = Path(BASE_DIR / "domain" / "web" / "templates")
version = importlib.metadata.version(DEFAULT_MODULE_NAME)


class ServerSettings(BaseSettings):
    """Server configurations."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="SERVER_", case_sensitive=False
    )

    APP_LOC: str = "app.asgi:create_app"
    """Path to app executable, or factory."""
    APP_LOC_IS_FACTORY: bool = True
    """Indicate if APP_LOC points to an executable or factory."""
    HOST: str = "localhost"
    """Server network host."""
    KEEPALIVE: int = 65
    """Seconds to hold connections open (65 is > AWS lb idle timeout)."""
    PORT: int = 8000
    """Server port."""
    RELOAD: bool | None = True
    """Turn on hot reloading."""
    RELOAD_DIRS: str = f"{BASE_DIR}"
    """Directories to watch for reloading."""
    HTTP_WORKERS: int | None = None
    """Number of HTTP Worker processes to be spawned by Uvicorn."""
    LIVE_API_KEY: str = ""
    """Live API key. for LiveKit server"""
    LIVE_API_SECRET: str = ""
    """Live API Secret. for LiveKit server"""
    LIVE_API_URL: str = ""
    """Zulip API URL. for zulip server"""
    ZULIP_API_URL: str = ""
    """Zulip Send Message API URL. for zulip server"""
    ZULIP_SEND_MESSAGE_URL: str = ""
    """Zulip Create Stream API URL. for zulip server"""
    ZULIP_CREATE_STREAM_URL: str = ""
    """Zulip Update Message API URL. for zulip server"""
    ZULIP_UPDATE_MESSAGE_URL: str = ""
    """Zulip Delete Message API URL. for zulip server"""
    ZULIP_DELETE_MESSAGE_URL: str = ""
    """Zulip Bot Email Address. for zulip server"""
    ZULIP_EMAIL_ADDRESS: str = ""
    """Zulip Bot API key. for zulip server"""
    ZULIP_API_KEY: str = ""
    """Zulip admins. for zulip server"""
    ZULIP_ADMIN_EMAIL: list[str] = ["phyoakl@hexcode.tech"]


class AppSettings(BaseSettings):
    """Generic application settings.`

    These settings are returned as json by the healthcheck endpoint, so
    do not include any sensitive values here, or if you do ensure to
    exclude them from serialization in the `model_config` object.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="APP_", case_sensitive=False
    )

    BUILD_NUMBER: str = ""
    """Identifier for CI build."""
    DEBUG: bool = False
    """Run `Litestar` with `debug=True`."""
    ENVIRONMENT: str = "prod"
    """'dev', 'prod', etc."""
    TEST_ENVIRONMENT_NAME: str = "test"
    """Value of ENVIRONMENT used to determine if running tests.

    This should be the value of `ENVIRONMENT` in `tests.env`.
    """
    LOCAL_ENVIRONMENT_NAME: str = "local"
    """Value of ENVIRONMENT used to determine if running in local development
    mode.

    This should be the value of `ENVIRONMENT` in your local `.env` file.
    """
    NAME: str = "app"
    """Application name."""
    SECRET_KEY: str = "ASDF12344"
    """Number of HTTP Worker processes to be spawned by Uvicorn."""
    JWT_ENCRYPTION_ALGORITHM: str = "HS256"
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    STATIC_URL: str = "/static/"
    CSRF_COOKIE_NAME: str = "csrftoken"
    CSRF_COOKIE_SECURE: bool = False
    """Default URL where static assets are located."""
    STATIC_DIR: Path = STATIC_DIR
    DEV_MODE: bool = False

    @property
    def slug(self) -> str:
        """Return a slugified name.

        Returns:
            `self.NAME`, all lowercase and hyphens instead of spaces.
        """
        return utils.slugify(self.NAME)

    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(
        cls,
        value: str | list[str],
    ) -> list[str] | str:
        """Parse a list of origins."""
        if isinstance(value, list):
            return value
        if isinstance(value, str) and not value.startswith("["):
            return [host.strip() for host in value.split(",")]
        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            return list(value)
        raise ValueError(value)

    @field_validator("SECRET_KEY")
    def generate_secret_key(
        cls,
        value: str | None,
    ) -> str:
        """Generate a secret key."""
        if value is None:
            return os.urandom(32).decode()
        return value


class LogSettings(BaseSettings):
    """Logging config for the application."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="LOG_")

    # https://stackoverflow.com/a/1845097/6560549
    EXCLUDE_PATHS: str = r"\A(?!x)x"
    """Regex to exclude paths from logging."""
    HTTP_EVENT: str = "HTTP"
    """Log event name for logs from Litestar handlers."""
    INCLUDE_COMPRESSED_BODY: bool = False
    """Include 'body' of compressed responses in log output."""
    LEVEL: int = 20
    """Stdlib log levels.

    Only emit logs at this level, or higher.
    """
    OBFUSCATE_COOKIES: set[str] = {"session"}
    """Request cookie keys to obfuscate."""
    OBFUSCATE_HEADERS: set[str] = {"Authorization", "X-API-KEY"}
    """Request header keys to obfuscate."""
    JOB_FIELDS: list[str] = [
        "function",
        "kwargs",
        "key",
        "scheduled",
        "attempts",
        "completed",
        "queued",
        "started",
        "result",
        "error",
    ]
    """Attributes of the SAQ.

    [`Job`](https://github.com/tobymao/saq/blob/master/saq/job.py) to be
    logged.
    """
    REQUEST_FIELDS: list[RequestExtractorField] = [
        "path",
        "method",
        # "headers",
        # "cookies",
        "query",
        "path_params",
        # "body",
    ]
    """Attributes of the [Request][litestar.connection.request.Request] to be
    logged."""
    RESPONSE_FIELDS: list[ResponseExtractorField] = [
        "status_code",
        # "cookies",
        # "headers",
        # "body",
    ]
    """Attributes of the [Response][litestar.response.Response] to be
    logged."""
    WORKER_EVENT: str = "Worker"
    """Log event name for logs from SAQ worker."""
    SAQ_LEVEL: int = 50
    """Level to log SAQ logs."""
    SQLALCHEMY_LEVEL: int = 30
    """Level to log SQLAlchemy logs."""
    UVICORN_ACCESS_LEVEL: int = 30
    """Level to log uvicorn access logs."""
    UVICORN_ERROR_LEVEL: int = 20
    """Level to log uvicorn error logs."""


# noinspection PyUnresolvedReferences
class OpenAPISettings(BaseSettings):
    """Configures OpenAPI for the application."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="OPENAPI_", case_sensitive=False
    )

    CONTACT_NAME: str = "Hexcode Technologies"
    """Name of contact on document."""
    CONTACT_EMAIL: str = "admin"
    """Email for contact on document."""
    TITLE: str | None = "Sprintlog"
    """Document title."""
    VERSION: str = "v1.0"
    """Document version."""
    LOCAL_CDN: str | None


class HTTPClientSettings(BaseSettings):
    """HTTP Client configurations."""

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_prefix = "HTTP_"

    BACKOFF_MAX: float = 60
    BACKOFF_MIN: float = 0
    EXPONENTIAL_BACKOFF_BASE: float = 2
    EXPONENTIAL_BACKOFF_MULTIPLIER: float = 1


class WorkerSettings(BaseSettings):
    """Global SAQ Job configuration."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="WORKER_", case_sensitive=False
    )

    JOB_TIMEOUT: int = 10
    """Max time a job can run for, in seconds.

    Set to `0` for no timeout.
    """
    JOB_HEARTBEAT: int = 0
    """Max time a job can survive without emitting a heartbeat. `0` to disable.

    `job.update()` will trigger a heartbeat.
    """
    JOB_RETRIES: int = 10
    """Max attempts for any job."""
    JOB_TTL: int = 600
    """Lifetime of available job information, in seconds.

    0: indefinite
    -1: disabled (no info retained)
    """
    JOB_RETRY_DELAY: float = 1.0
    """Seconds to delay before retrying a job."""
    JOB_RETRY_BACKOFF: bool | float = 60
    """If true, use exponential backoff for retry delays.

    - The first retry will have whatever retry_delay is.
    - The second retry will have retry_delay*2. The third retry will have retry_delay*4. And so on.
    - This always includes jitter, where the final retry delay is a random number between 0 and the calculated retry delay.
    - If retry_backoff is set to a number, that number is the maximum retry delay, in seconds."
    """
    CONCURRENCY: int = 10
    """The number of concurrent jobs allowed to execute per worker.

    Default is set to 10.
    """
    WEB_ENABLED: bool = False
    """If true, the worker admin UI is launched on worker startup.."""
    WEB_PORT: int = 8081
    """Port to use for the worker web UI."""
    INIT_METHOD: Literal["integrated", "standalone"] = "integrated"
    """Initialization method for the worker process."""


class DatabaseSettings(BaseSettings):
    """Configures the database for the application."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="DB_", case_sensitive=False
    )

    ECHO: bool = False
    """Enable SQLAlchemy engine logs."""
    ECHO_POOL: bool | Literal["debug"] = False
    """Enable SQLAlchemy connection pool logs."""
    POOL_DISABLE: bool = False
    """Disable SQLAlchemy pooling, same as setting pool to.

    [`NullPool`][sqlalchemy.pool.NullPool].
    """
    POOL_MAX_OVERFLOW: int = 10
    """See [`max_overflow`][sqlalchemy.pool.QueuePool]."""
    POOL_SIZE: int = 5
    """See [`pool_size`][sqlalchemy.pool.QueuePool]."""
    POOL_TIMEOUT: int = 30
    """See [`timeout`][sqlalchemy.pool.QueuePool]."""
    POOL_RECYCLE: int = 300
    POOL_PRE_PING: bool = False
    CONNECT_ARGS: dict[str, Any] = {}
    URL: str = "postgresql+asyncpg://postgres:mysecretpassword@localhost:5432/postgres"
    EXT_URL: str = "postgresql+asyncpg://postgres:mysecretpassword@localhost:5432/postgres"

    ENGINE: str | None = None
    USER: str | None = None
    PASSWORD: str | None = None
    HOST: str | None = None
    PORT: int | None = None
    NAME: str | None = None
    MIGRATION_CONFIG: str = f"{BASE_DIR}/lib/db/alembic.ini"
    MIGRATION_PATH: str = f"{BASE_DIR}/lib/db/migrations"
    MIGRATION_DDL_VERSION_TABLE: str = "ddl_version"


class RedisSettings(BaseSettings):
    """Redis settings for the application."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="REDIS_")

    URL: str = "redis://localhost:6379/0"
    """A Redis connection URL."""
    DB: int | None = None
    """Redis DB ID (optional)"""
    PORT: int | None = None
    """Redis port (optional)"""
    SOCKET_CONNECT_TIMEOUT: int = 5
    """Length of time to wait (in seconds) for a connection to become
    active."""
    HEALTH_CHECK_INTERVAL: int = 5
    """Length of time to wait (in seconds) before testing connection health."""
    SOCKET_KEEPALIVE: int = 5
    """Length of time to wait (in seconds) between keepalive commands."""


class PluginSettings(BaseSettings):
    """Server configurations."""

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_prefix = "PLUGIN_"

    """Disable or enable zulip plugin"""
    PLUGINS: list[str]


@lru_cache
def load_settings() -> (
    tuple[
        AppSettings,
        RedisSettings,
        DatabaseSettings,
        OpenAPISettings,
        ServerSettings,
        LogSettings,
        WorkerSettings,
        PluginSettings,
    ]
):
    """Load Settings file.

    As an example, I've commented out how you might go about injecting secrets into the environment for production.

    This fetches a `.env` configuration from a Google secret and configures the environment with those variables.

    ```python
    secret_id = os.environ.get("ENV_SECRETS", None)
    env_file_exists = os.path.isfile(f"{os.curdir}/.env")
    local_service_account_exists = os.path.isfile(f"{os.curdir}/service_account.json")
    if local_service_account_exists:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"
    project_id = os.environ.get("GOOGLE_PROJECT_ID", None)
    if project_id is None:
        _, project_id = google.auth.default()
        os.environ["GOOGLE_PROJECT_ID"] = project_id
    if not env_file_exists and secret_id:
        secret = secret_manager.get_secret(project_id, secret_id)
        load_dotenv(stream=io.StringIO(secret))

    try:
        settings = ...  # existing code below
    except:
        ...
    return settings
    ```
    Returns:
        Settings: application settings
    """
    env_file = Path(f"{os.curdir}/.env")
    if env_file.is_file():
        load_dotenv(env_file)
    try:
        """Override Application reload dir."""
        server: ServerSettings = ServerSettings.model_validate(
            {"HOST": "0.0.0.0", "RELOAD_DIRS": str(BASE_DIR)},  # noqa: S104
        )
        app: AppSettings = AppSettings.model_validate({})
        redis: RedisSettings = RedisSettings.model_validate({})
        db: DatabaseSettings = DatabaseSettings.model_validate({})
        openapi: OpenAPISettings = OpenAPISettings.model_validate({})
        log: LogSettings = LogSettings.model_validate({})
        worker: WorkerSettings = WorkerSettings.model_validate({})
        plugin: PluginSettings = PluginSettings.model_validate({})
        HTTPClientSettings.model_validate({})

    except ValidationError as e:
        print("Could not load settings. %s", e)  # noqa: T201
        raise e from e
    return (
        app,
        redis,
        db,
        openapi,
        server,
        log,
        worker,
        plugin,
    )


(
    app,
    redis,
    db,
    openapi,
    server,
    log,
    worker,
    plugin,
) = load_settings()
