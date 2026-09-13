from collections.abc import Sequence

from loredeck.game.decks.repositories.base import DeckRepository, DeckSummary


class ListActiveDecksUseCase:
    def __init__(self, repository: DeckRepository) -> None:
        self._repository = repository

    async def execute(self) -> Sequence[DeckSummary]:
        return await self._repository.list_active()
