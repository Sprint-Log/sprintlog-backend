"""User Account Controllers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.backlogs.models import Service
from app.lib import log

__all__ = ["provides_service"]


logger = log.get_logger()

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession


async def provides_service(db_session: AsyncSession) -> AsyncGenerator[Service, None]:
    """Construct repository and service objects for the request."""
    async with Service.new(
        session=db_session,
    ) as service:
        try:
            yield service
        finally:
            ...
