from collections.abc import Callable

from loredeck.ai.enums import AIProviderName
from loredeck.ai.exceptions import InvalidAIConfigurationError, UnsupportedAIProviderError
from loredeck.ai.providers import AIProvider, OpenAIProvider
from loredeck.shared.config import Settings

ProviderBuilder = Callable[[Settings], AIProvider]


def _build_openai_provider(settings: Settings) -> AIProvider:
    if settings.openai_api_key is None or settings.openai_model is None:
        raise InvalidAIConfigurationError("OpenAI provider configuration is incomplete")
    return OpenAIProvider(
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        timeout_seconds=settings.openai_timeout_seconds,
        max_retries=settings.openai_max_retries,
        story_max_characters=settings.ai_story_max_characters,
        summary_max_characters=settings.ai_summary_max_characters,
    )


PROVIDER_BUILDERS: dict[AIProviderName, ProviderBuilder] = {
    AIProviderName.OPENAI: _build_openai_provider,
}


def create_ai_provider(settings: Settings) -> AIProvider:
    try:
        builder = PROVIDER_BUILDERS[settings.ai_provider]
    except KeyError as error:
        raise UnsupportedAIProviderError("The configured AI provider is unsupported") from error
    return builder(settings)
