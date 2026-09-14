from typing import Protocol

from loredeck.ai.schemas import GenerateReadingRequest, GenerateReadingResult


class AIProvider(Protocol):
    """Provider-independent contract for generating a card reading."""

    async def generate_reading(
        self,
        request: GenerateReadingRequest,
    ) -> GenerateReadingResult: ...
