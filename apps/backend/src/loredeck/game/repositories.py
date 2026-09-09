from collections.abc import Sequence
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from loredeck.shared.models import CardModel, DeckModel


class ReadingRepository(Protocol):
    async def get_deck_active_status(self, deck_id: int) -> bool | None: ...

    async def list_active_card_ids(self, deck_id: int) -> Sequence[int]: ...

    async def get_active_cards_by_ids(
        self,
        deck_id: int,
        card_ids: Sequence[int],
    ) -> Sequence[CardModel]: ...


class SqlAlchemyReadingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_deck_active_status(self, deck_id: int) -> bool | None:
        result = await self._session.execute(
            select(DeckModel.is_active).where(DeckModel.id == deck_id)
        )
        return result.scalar_one_or_none()

    async def list_active_card_ids(self, deck_id: int) -> Sequence[int]:
        result = await self._session.scalars(
            select(CardModel.id).where(
                CardModel.deck_id == deck_id,
                CardModel.is_active.is_(True),
            )
        )
        return result.all()

    async def get_active_cards_by_ids(
        self,
        deck_id: int,
        card_ids: Sequence[int],
    ) -> Sequence[CardModel]:
        result = await self._session.scalars(
            select(CardModel).where(
                CardModel.deck_id == deck_id,
                CardModel.is_active.is_(True),
                CardModel.id.in_(card_ids),
            )
        )
        return result.all()
