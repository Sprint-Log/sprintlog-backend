# pylint: disable=protected-access
from __future__ import annotations

import random
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from litestar.constants import SCOPE_STATE_NAMESPACE
from litestar.contrib.sqlalchemy.plugins.init.config.common import SESSION_SCOPE_KEY
from sqlalchemy.ext.asyncio import AsyncSession

from app.lib import db

if TYPE_CHECKING:
    from litestar import Litestar
    from litestar.types import HTTPResponseStartEvent, HTTPScope


async def test_before_send_handler_success_response(
    app: Litestar, http_response_start: HTTPResponseStartEvent, http_scope: HTTPScope
) -> None:
    """Test that the session is committed given a success response."""
    mock_session = MagicMock(spec=AsyncSession)
    namespace = http_scope["state"].setdefault(SCOPE_STATE_NAMESPACE, {})
    namespace.update({SESSION_SCOPE_KEY: mock_session})
    http_scope["state"][SESSION_SCOPE_KEY] = mock_session
    http_response_start["status"] = random.randint(200, 299)  # noqa: S311
    await db.before_send_handler(http_response_start, http_scope)
    mock_session.commit.assert_awaited_once()


async def test_before_send_handler_error_response(
    app: Litestar, http_response_start: HTTPResponseStartEvent, http_scope: HTTPScope
) -> None:
    """Test that the session is committed given a success response."""
    mock_session = MagicMock(spec=AsyncSession)
    namespace = http_scope["state"].setdefault(SCOPE_STATE_NAMESPACE, {})
    namespace.update({SESSION_SCOPE_KEY: mock_session})
    http_scope["state"][SESSION_SCOPE_KEY] = mock_session
    http_response_start["status"] = random.randint(300, 599)  # noqa: S311
    await db.before_send_handler(http_response_start, http_scope)
    mock_session.rollback.assert_awaited_once()
