import secrets
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from loredeck.game.exceptions import (
    DeckNotFoundError,
    InactiveDeckError,
    InsufficientActiveCardsError,
)
from loredeck.game.repositories import ReadingRepository
from loredeck.shared.models import CardModel


class Spread(StrEnum):
    ONE_CARD = "one_card"
    THREE_CARD = "three_card"


class ReadingPosition(StrEnum):
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


class Orientation(StrEnum):
    UPRIGHT = "upright"


@dataclass(frozen=True)
class PublicCard:
    title: str
    description: str | None
    number: int | None
    image_path: str | None


@dataclass(frozen=True)
class DrawnCard:
    position: ReadingPosition
    orientation: Orientation
    card: PublicCard
    story: str = ""


@dataclass(frozen=True)
class ReadingResult:
    cards: Sequence[DrawnCard]
    summary: str = ""


POSITIONS_BY_SPREAD: dict[Spread, tuple[ReadingPosition, ...]] = {
    Spread.ONE_CARD: (ReadingPosition.PRESENT,),
    Spread.THREE_CARD: (
        ReadingPosition.PAST,
        ReadingPosition.PRESENT,
        ReadingPosition.FUTURE,
    ),
}


class DrawReadingUseCase:
    def __init__(self, repository: ReadingRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        *,
        deck_id: int,
        spread: Spread,
        question: str | None,
    ) -> ReadingResult:
        del question  # Reserved for future story generation; accepted by the public contract.

        deck_is_active = await self._repository.get_deck_active_status(deck_id)
        if deck_is_active is None:
            raise DeckNotFoundError
        if not deck_is_active:
            raise InactiveDeckError

        count = 1 if spread == Spread.ONE_CARD else 3
        active_card_ids = list(await self._repository.list_active_card_ids(deck_id))
        if len(active_card_ids) < count:
            raise InsufficientActiveCardsError

        selected_ids = secrets.SystemRandom().sample(active_card_ids, k=count)
        cards = await self._repository.get_active_cards_by_ids(deck_id, selected_ids)
        cards_by_id = {card.id: card for card in cards}
        if any(card_id not in cards_by_id for card_id in selected_ids):
            raise InsufficientActiveCardsError
        selected_cards = [cards_by_id[card_id] for card_id in selected_ids]

        return ReadingResult(
            cards=tuple(
                self._to_drawn_card(position, card)
                for position, card in zip(
                    POSITIONS_BY_SPREAD[spread],
                    selected_cards,
                    strict=True,
                )
            )
        )

    @staticmethod
    def _to_drawn_card(position: ReadingPosition, card: CardModel) -> DrawnCard:
        return DrawnCard(
            position=position,
            orientation=Orientation.UPRIGHT,
            card=PublicCard(
                title=card.title,
                description=card.description,
                number=card.number,
                image_path=card.image_path,
            ),
        )
