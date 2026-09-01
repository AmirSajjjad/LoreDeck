import pytest
from sqlalchemy import text

from loredeck.db.session import get_session_factory


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_connection() -> None:
    session_factory = get_session_factory()

    async with session_factory() as session:
        result = await session.execute(text("SELECT 1"))

    assert result.scalar_one() == 1
