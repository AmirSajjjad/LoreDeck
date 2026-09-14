from dataclasses import dataclass

from pydantic import SecretStr

from loredeck.ai.exceptions import AIProviderUnavailableError
from loredeck.ai.schemas import GenerateReadingRequest, GenerateReadingResult


@dataclass(frozen=True)
class OpenAIProvider:
    api_key: SecretStr
    model: str
    timeout_seconds: float
    max_retries: int

    async def generate_reading(
        self,
        request: GenerateReadingRequest,
    ) -> GenerateReadingResult:
        del request
        raise AIProviderUnavailableError("The OpenAI provider is not implemented")
