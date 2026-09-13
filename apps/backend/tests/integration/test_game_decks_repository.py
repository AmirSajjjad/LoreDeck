from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from loredeck.game.decks.repositories.base import DeckSummary
from loredeck.game.decks.repositories.sqlalchemy import SqlAlchemyDeckRepository
from loredeck.shared.config import get_settings
from loredeck.shared.models import DeckModel

pytestmark = pytest.mark.integration


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(get_settings().database_url, poolclass=NullPool)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        async with AsyncSession(bind=connection, expire_on_commit=False) as database_session:
            yield database_session
        if transaction.is_active:
            await transaction.rollback()
    await engine.dispose()


@pytest.mark.asyncio
async def test_list_active_decks_filters_and_orders_without_loading_cards(
    session: AsyncSession,
) -> None:
    token = uuid4().hex
    active_first = DeckModel(title=f"Active first {token}", is_active=True)
    inactive = DeckModel(title=f"Inactive {token}", is_active=False)
    active_second = DeckModel(title=f"Active second {token}", is_active=True)
    session.add_all([active_first, inactive, active_second])
    await session.flush()

    decks = await SqlAlchemyDeckRepository(session).list_active()
    created_ids = {active_first.id, inactive.id, active_second.id}
    created = [deck for deck in decks if deck.id in created_ids]

    assert created == [
        DeckSummary(id=active_first.id, title=active_first.title),
        DeckSummary(id=active_second.id, title=active_second.title),
    ]
    assert inactive.id not in {deck.id for deck in decks}
