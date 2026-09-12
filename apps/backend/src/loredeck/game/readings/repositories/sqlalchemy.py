from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from loredeck.game.readings.repositories.base import NewReadingHistory
from loredeck.shared.models import CardModel, DeckModel, UserCardHistoryModel


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
        self, deck_id: int, card_ids: Sequence[int]
    ) -> Sequence[CardModel]:
        result = await self._session.scalars(
            select(CardModel).where(
                CardModel.deck_id == deck_id,
                CardModel.is_active.is_(True),
                CardModel.id.in_(card_ids),
            )
        )
        return result.all()

    async def add_history(self, history: NewReadingHistory) -> None:
        self._session.add(
            UserCardHistoryModel(
                user_id=history.user_id,
                question=history.question,
                deck_id=history.deck_id,
                first_card_id=history.first_card_id,
                first_story=history.first_story,
                second_card_id=history.second_card_id,
                second_story=history.second_story,
                third_card_id=history.third_card_id,
                third_story=history.third_story,
                summary=history.summary,
            )
        )
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
