"""User Account Controllers."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import aiosql

from app.contrib.aiosql import AiosqlQueryManager
from app.lib.settings import BASE_DIR

__all__ = ["provides_analytic_queries"]


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession


analytics_queries = aiosql.from_path(Path(BASE_DIR / "domain" / "analytics" / "sql"), driver_adapter="asyncpg")


async def provides_analytic_queries(
    db_session: AsyncSession,
) -> AsyncGenerator[AiosqlQueryManager, None]:
    """Construct repository and service objects for the request."""
    async with AiosqlQueryManager.from_session(analytics_queries, session=db_session) as query_manager:
        yield query_manager
