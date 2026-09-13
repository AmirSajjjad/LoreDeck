from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from loredeck.game.decks.repositories.base import DeckSummary
from loredeck.shared.models import DeckModel


class SqlAlchemyDeckRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_active(self) -> Sequence[DeckSummary]:
        rows = await self._session.execute(
            select(DeckModel.id, DeckModel.title)
            .where(DeckModel.is_active.is_(True))
            .order_by(DeckModel.id.asc())
        )
        return [DeckSummary(id=row.id, title=row.title) for row in rows]
