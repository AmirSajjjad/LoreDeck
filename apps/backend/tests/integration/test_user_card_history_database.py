from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

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


async def create_history_dependencies(
    session: AsyncSession,
) -> tuple[UserModel, DeckModel, tuple[CardModel, CardModel, CardModel]]:
    token = uuid4().hex
    user = UserModel(username=f"user-{token}", password_hash="hashed-password")
    deck = DeckModel(title=f"Deck {token}", description=None, is_active=True)
    session.add_all([user, deck])
    await session.flush()

    def create_card(number: int) -> CardModel:
        return CardModel(
            deck_id=deck.id,
            title=f"Card {number}",
            description=None,
            number=number,
            image_path=None,
            attributes={},
            is_active=True,
        )

    cards = (
        create_card(1),
        create_card(2),
        create_card(3),
    )
    session.add_all(cards)
    await session.flush()
    return user, deck, cards


@pytest.mark.asyncio
async def test_valid_one_card_history_can_be_stored(session: AsyncSession) -> None:
    user, deck, cards = await create_history_dependencies(session)
    history = UserCardHistoryModel(
        user_id=user.id,
        deck_id=deck.id,
        first_card_id=cards[0].id,
        question=None,
        first_story=None,
        second_card_id=None,
        second_story=None,
        third_card_id=None,
        third_story=None,
        summary=None,
    )
    session.add(history)

    await session.flush()
    await session.refresh(history)

    assert history.id is not None
    assert history.created_at.utcoffset() is not None
    assert history.second_card_id is None
    assert history.third_card_id is None


@pytest.mark.asyncio
async def test_valid_three_card_history_can_be_stored(session: AsyncSession) -> None:
    user, deck, cards = await create_history_dependencies(session)
    history = UserCardHistoryModel(
        user_id=user.id,
        deck_id=deck.id,
        first_card_id=cards[0].id,
        first_story="First",
        second_card_id=cards[1].id,
        second_story="Second",
        third_card_id=cards[2].id,
        third_story="Third",
        question="What next?",
        summary="Summary",
    )
    session.add(history)

    await session.flush()

    assert history.id is not None
    assert history.created_at.utcoffset() is not None
    assert (history.first_card_id, history.second_card_id, history.third_card_id) == tuple(
        card.id for card in cards
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("positions"),
    [
        (0, 0, None),
        (0, 1, 0),
        (0, 1, 1),
    ],
)
async def test_duplicate_cards_are_rejected(
    session: AsyncSession,
    positions: tuple[int, int, int | None],
) -> None:
    user, deck, cards = await create_history_dependencies(session)
    first, second, third = positions
    history = UserCardHistoryModel(
        user_id=user.id,
        deck_id=deck.id,
        first_card_id=cards[first].id,
        second_card_id=cards[second].id,
        third_card_id=cards[third].id if third is not None else None,
    )
    session.add(history)

    with pytest.raises(IntegrityError):
        await session.flush()


@pytest.mark.asyncio
async def test_third_card_without_second_card_is_rejected(session: AsyncSession) -> None:
    user, deck, cards = await create_history_dependencies(session)
    history = UserCardHistoryModel(
        user_id=user.id,
        deck_id=deck.id,
        first_card_id=cards[0].id,
        second_card_id=None,
        third_card_id=cards[2].id,
    )
    session.add(history)

    with pytest.raises(IntegrityError):
        await session.flush()
