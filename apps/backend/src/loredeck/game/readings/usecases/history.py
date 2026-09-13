import logging
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from loredeck.game.readings.repositories.history import ReadingHistoryRepository
from loredeck.game.readings.usecases.create_reading import (
    Orientation,
    PublicCard,
    ReadingPosition,
    Spread,
)
from loredeck.shared.models import CardModel, UserCardHistoryModel

logger = logging.getLogger(__name__)


class HistoryNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class HistoryDeck:
    id: int
    title: str


@dataclass(frozen=True)
class HistoryListItem:
    id: int
    created_at: datetime
    question: str | None
    deck: HistoryDeck
    spread: Spread


@dataclass(frozen=True)
class HistoryListResult:
    items: Sequence[HistoryListItem]
    total: int
    limit: int
    offset: int


@dataclass(frozen=True)
class HistoricalCard:
    position: ReadingPosition
    orientation: Orientation
    card: PublicCard
    story: str | None


@dataclass(frozen=True)
class HistoryDetail:
    id: int
    created_at: datetime
    question: str | None
    deck: HistoryDeck
    spread: Spread
    cards: Sequence[HistoricalCard]
    summary: str | None


def history_spread(history: UserCardHistoryModel) -> Spread:
    if history.second_card_id is None and history.third_card_id is None:
        return Spread.ONE_CARD
    if history.second_card_id is not None and history.third_card_id is not None:
        return Spread.THREE_CARD
    raise ValueError("Unsupported history card slots")


def public_card(card: CardModel) -> PublicCard:
    return PublicCard(
        title=card.title,
        description=card.description,
        number=card.number,
        image_path=card.image_path,
    )


class ListReadingHistoryUseCase:
    def __init__(self, repository: ReadingHistoryRepository) -> None:
        self._repository = repository

    async def execute(self, user_id: int, *, limit: int, offset: int) -> HistoryListResult:
        records = await self._repository.list_for_user(user_id, limit=limit, offset=offset)
        if records.excluded_count:
            logger.warning(
                "Excluded %d unsupported reading history records", records.excluded_count
            )
        return HistoryListResult(
            items=tuple(
                HistoryListItem(
                    id=history.id,
                    created_at=history.created_at,
                    question=history.question,
                    deck=HistoryDeck(id=history.deck.id, title=history.deck.title),
                    spread=history_spread(history),
                )
                for history in records.items
            ),
            total=records.total,
            limit=limit,
            offset=offset,
        )


class GetReadingHistoryUseCase:
    def __init__(self, repository: ReadingHistoryRepository) -> None:
        self._repository = repository

    async def execute(self, user_id: int, history_id: int) -> HistoryDetail:
        history = await self._repository.get_for_user(user_id, history_id)
        if history is None:
            raise HistoryNotFoundError

        spread = history_spread(history)
        if spread == Spread.ONE_CARD:
            card_slots = ((ReadingPosition.PRESENT, history.first_card, history.first_story),)
        else:
            assert history.second_card is not None and history.third_card is not None
            card_slots = (
                (ReadingPosition.PAST, history.first_card, history.first_story),
                (ReadingPosition.PRESENT, history.second_card, history.second_story),
                (ReadingPosition.FUTURE, history.third_card, history.third_story),
            )

        return HistoryDetail(
            id=history.id,
            created_at=history.created_at,
            question=history.question,
            deck=HistoryDeck(id=history.deck.id, title=history.deck.title),
            spread=spread,
            cards=tuple(
                HistoricalCard(
                    position=position,
                    orientation=Orientation.UPRIGHT,
                    card=public_card(card),
                    story=story,
                )
                for position, card, story in card_slots
            ),
            summary=history.summary,
        )
