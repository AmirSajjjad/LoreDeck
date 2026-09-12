from collections.abc import Sequence
from typing import Protocol

from loredeck.shared.models import CardModel


class ReadingRepository(Protocol):
    async def get_deck_active_status(self, deck_id: int) -> bool | None: ...

    async def list_active_card_ids(self, deck_id: int) -> Sequence[int]: ...

    async def get_active_cards_by_ids(
        self, deck_id: int, card_ids: Sequence[int]
    ) -> Sequence[CardModel]: ...
