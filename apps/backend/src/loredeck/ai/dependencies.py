from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from loredeck.ai.factory import create_ai_provider
from loredeck.ai.providers.base import AIProvider
from loredeck.ai.service import AIService
from loredeck.shared.config import get_settings


@lru_cache
def get_ai_provider() -> AIProvider:
    return create_ai_provider(get_settings())


def get_ai_service(
    provider: Annotated[AIProvider, Depends(get_ai_provider)],
) -> AIService:
    settings = get_settings()
    return AIService(
        provider,
        story_max_characters=settings.ai_story_max_characters,
        summary_max_characters=settings.ai_summary_max_characters,
    )
