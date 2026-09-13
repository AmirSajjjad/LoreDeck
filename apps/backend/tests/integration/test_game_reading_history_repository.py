from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from loredeck.game.readings.repositories.history import SqlAlchemyReadingHistoryRepository
from loredeck.shared.config import get_settings
from loredeck.shared.models import CardModel, DeckModel, UserCardHistoryModel, UserModel

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
async def test_history_repository_scopes_orders_paginates_and_loads_detail(
    session: AsyncSession,
) -> None:
    token = uuid4().hex
    owner = UserModel(username=f"owner-{token}", password_hash="hash")
    other = UserModel(username=f"other-{token}", password_hash="hash")
    deck = DeckModel(title=f"Deck {token}", is_active=True)
    session.add_all([owner, other, deck])
    await session.flush()
    cards = [
        CardModel(deck_id=deck.id, title=f"Card {index}", attributes={}, is_active=True)
        for index in range(3)
    ]
    session.add_all(cards)
    await session.flush()
    now = datetime.now(UTC)
    older = UserCardHistoryModel(
        user_id=owner.id,
        deck_id=deck.id,
        first_card_id=cards[0].id,
        created_at=now - timedelta(days=1),
    )
    newer = UserCardHistoryModel(
        user_id=owner.id,
        deck_id=deck.id,
        first_card_id=cards[0].id,
        second_card_id=cards[1].id,
        third_card_id=cards[2].id,
        created_at=now,
    )
    foreign = UserCardHistoryModel(
        user_id=other.id,
        deck_id=deck.id,
        first_card_id=cards[0].id,
        created_at=now + timedelta(days=1),
    )
    session.add_all([older, newer, foreign])
    await session.flush()

    repository = SqlAlchemyReadingHistoryRepository(session)
    page = await repository.list_for_user(owner.id, limit=1, offset=0)

    assert page.total == 2
    assert [item.id for item in page.items] == [newer.id]
    assert page.items[0].deck.title == deck.title
    detail = await repository.get_for_user(owner.id, newer.id)
    assert detail is not None and detail.third_card is not None
    assert await repository.get_for_user(owner.id, foreign.id) is None
