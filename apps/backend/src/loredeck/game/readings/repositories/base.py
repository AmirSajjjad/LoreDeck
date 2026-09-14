from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from loredeck.shared.models import CardModel


@dataclass(frozen=True)
class NewReadingHistory:
    user_id: int
    question: str | None
    deck_id: int
    first_card_id: int
    first_story: str | None
    second_card_id: int | None
    second_story: str | None
    third_card_id: int | None
    third_story: str | None
    summary: str | None


class ReadingRepository(Protocol):
    async def get_deck_active_status(self, deck_id: int) -> bool | None: ...

    async def list_active_card_ids(self, deck_id: int) -> Sequence[int]: ...

    async def get_active_cards_by_ids(
        self, deck_id: int, card_ids: Sequence[int]
    ) -> Sequence[CardModel]: ...

    async def release_selection_transaction(self) -> None: ...

    async def add_history(self, history: NewReadingHistory) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
