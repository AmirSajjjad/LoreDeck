import secrets
from collections.abc import Sequence
from dataclasses import dataclass

from loredeck.game.readings.repositories.base import NewReadingHistory, ReadingRepository
from loredeck.shared.models import CardModel
from loredeck.shared.readings import CardOrientation as Orientation
from loredeck.shared.readings import ReadingPosition
from loredeck.shared.readings import ReadingSpread as Spread


class DeckNotFoundError(Exception):
    """Raised when a requested deck does not exist."""


class InactiveDeckError(Exception):
    """Raised when a requested deck is not active."""


class InsufficientActiveCardsError(Exception):
    """Raised when a spread requires more active cards than are available."""


class ReadingPersistenceError(Exception):
    """Raised when an authenticated reading cannot be saved."""


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
        user_id: int | None = None,
    ) -> ReadingResult:
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

        result = ReadingResult(
            cards=tuple(
                self._to_drawn_card(position, cards_by_id[card_id])
                for position, card_id in zip(POSITIONS_BY_SPREAD[spread], selected_ids, strict=True)
            )
        )
        if user_id is not None:
            await self._save_history(
                user_id=user_id,
                question=question,
                deck_id=deck_id,
                selected_ids=selected_ids,
                result=result,
            )
        return result

    async def _save_history(
        self,
        *,
        user_id: int,
        question: str | None,
        deck_id: int,
        selected_ids: Sequence[int],
        result: ReadingResult,
    ) -> None:
        card_ids: tuple[int | None, int | None, int | None] = (
            selected_ids[0],
            selected_ids[1] if len(selected_ids) > 1 else None,
            selected_ids[2] if len(selected_ids) > 2 else None,
        )
        stories: tuple[str | None, str | None, str | None] = (
            result.cards[0].story,
            result.cards[1].story if len(result.cards) > 1 else None,
            result.cards[2].story if len(result.cards) > 2 else None,
        )
        try:
            await self._repository.add_history(
                NewReadingHistory(
                    user_id=user_id,
                    question=question,
                    deck_id=deck_id,
                    first_card_id=card_ids[0],
                    first_story=stories[0],
                    second_card_id=card_ids[1],
                    second_story=stories[1],
                    third_card_id=card_ids[2],
                    third_story=stories[2],
                    summary=result.summary,
                )
            )
            await self._repository.commit()
        except Exception as error:
            await self._repository.rollback()
            raise ReadingPersistenceError from error

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
