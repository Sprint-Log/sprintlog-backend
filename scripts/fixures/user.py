from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest
from httpx import AsyncClient
from litestar import Litestar
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.domain.accounts.models import User
from app.domain.security import auth
from app.domain.teams.models import Team

here = Path(__file__).parent


@pytest.fixture(name="sessionmaker")
def fx_session_maker_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture(name="session")
def fx_session(sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncSession:
    return sessionmaker()


@pytest.fixture(autouse=True)
async def _seed_db(
    engine: AsyncEngine,
    sessionmaker: async_sessionmaker[AsyncSession],
    raw_users: list[User | dict[str, Any]],
    raw_teams: list[Team | dict[str, Any]],
):
    """Populate test database with.

    Args:
        engine: The SQLAlchemy engine instance.
        sessionmaker: The SQLAlchemy sessionmaker factory.
        raw_users: Test users to add to the database
        raw_teams: Test teams to add to the database

    """

    from app.domain.accounts.services import UserService
    from app.domain.teams.services import TeamService
    from app.lib.db import orm  # pylint: disable=[import-outside-toplevel,unused-import]

    metadata = orm.DatabaseModel.registry.metadata
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    async with UserService.new(sessionmaker()) as users_service:
        await users_service.create_many(raw_users)
        await users_service.repository.session.commit()
    async with TeamService.new(sessionmaker()) as teams_services:
        for raw_team in raw_teams:
            await teams_services.create(raw_team)
        await teams_services.repository.session.commit()


@pytest.fixture(name="client")
async def fx_client(app: Litestar) -> AsyncIterator[AsyncClient]:
    """Async client that calls requests on the app.

    ```text
    ValueError: The future belongs to a different loop than the one specified as the loop argument
    ```
    """
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(name="superuser_token_headers")
def fx_superuser_token_headers() -> dict[str, str]:
    """Valid superuser token.

    ```text
    ValueError: The future belongs to a different loop than the one specified as the loop argument
    ```
    """
    return {"Authorization": f"Bearer {auth.create_token(identifier='admin@hexcode.tech')}"}


@pytest.fixture(name="user_token_headers")
def fx_user_token_headers() -> dict[str, str]:
    """Valid user token.

    ```text
    ValueError: The future belongs to a different loop than the one specified as the loop argument
    ```
    """
    return {"Authorization": f"Bearer {auth.create_token(identifier='user@example.com')}"}
