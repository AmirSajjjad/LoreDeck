from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class DeckSummary:
    id: int
    title: str


class DeckRepository(Protocol):
    async def list_active(self) -> Sequence[DeckSummary]: ...
