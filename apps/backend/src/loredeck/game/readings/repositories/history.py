from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from loredeck.shared.models import UserCardHistoryModel


@dataclass(frozen=True)
class HistoryRecords:
    items: Sequence[UserCardHistoryModel]
    total: int
    excluded_count: int


class ReadingHistoryRepository(Protocol):
    async def list_for_user(self, user_id: int, *, limit: int, offset: int) -> HistoryRecords: ...

    async def get_for_user(self, user_id: int, history_id: int) -> UserCardHistoryModel | None: ...


def valid_card_slots():
    return or_(
        and_(
            UserCardHistoryModel.second_card_id.is_(None),
            UserCardHistoryModel.third_card_id.is_(None),
        ),
        and_(
            UserCardHistoryModel.second_card_id.is_not(None),
            UserCardHistoryModel.third_card_id.is_not(None),
        ),
    )


class SqlAlchemyReadingHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_user(self, user_id: int, *, limit: int, offset: int) -> HistoryRecords:
        valid = valid_card_slots()
        items = await self._session.scalars(
            select(UserCardHistoryModel)
            .where(UserCardHistoryModel.user_id == user_id, valid)
            .options(joinedload(UserCardHistoryModel.deck))
            .order_by(
                UserCardHistoryModel.created_at.desc(),
                UserCardHistoryModel.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        total = await self._session.scalar(
            select(func.count(UserCardHistoryModel.id)).where(
                UserCardHistoryModel.user_id == user_id, valid
            )
        )
        excluded = await self._session.scalar(
            select(func.count(UserCardHistoryModel.id)).where(
                UserCardHistoryModel.user_id == user_id, ~valid
            )
        )
        return HistoryRecords(items=items.all(), total=total or 0, excluded_count=excluded or 0)

    async def get_for_user(self, user_id: int, history_id: int) -> UserCardHistoryModel | None:
        result = await self._session.scalars(
            select(UserCardHistoryModel)
            .where(
                UserCardHistoryModel.id == history_id,
                UserCardHistoryModel.user_id == user_id,
                valid_card_slots(),
            )
            .options(
                joinedload(UserCardHistoryModel.deck),
                joinedload(UserCardHistoryModel.first_card),
                joinedload(UserCardHistoryModel.second_card),
                joinedload(UserCardHistoryModel.third_card),
            )
        )
        return result.one_or_none()
