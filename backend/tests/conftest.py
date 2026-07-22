from collections.abc import AsyncGenerator
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_db_session
from app.main import app


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """
    Mock SQLAlchemy AsyncSession for unit testing without database daemon.
    """
    session = AsyncMock()
    session.execute = AsyncMock()
    session.scalars = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.add = MagicMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
async def client(
    mock_db_session: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    """
    HTTP client fixture using ASGITransport to bypass networking.
    """

    async def override_get_db_session():
        yield mock_db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    async with AsyncClient(
        transport=ASGITransport(app=cast(Any, app)), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
