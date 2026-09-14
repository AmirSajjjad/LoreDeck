import logging

from openai import (
    APIConnectionError,
    APIResponseValidationError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
)
from pydantic import BaseModel, ConfigDict, SecretStr, ValidationError

from loredeck.ai.exceptions import (
    AIError,
    AIProviderRefusalError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
    InvalidAIConfigurationError,
    InvalidAIProviderResponseError,
)
from loredeck.ai.prompts.tarot_reading import (
    TAROT_READING_INSTRUCTIONS,
    build_tarot_reading_input,
)
from loredeck.ai.schemas import GeneratedCardStory, GenerateReadingRequest, GenerateReadingResult

logger = logging.getLogger(__name__)
MAX_OUTPUT_TOKENS = 4096
MIN_OUTPUT_TOKENS = 256


class OpenAICardStory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card_id: int
    story: str


class OpenAITarotReadingOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cards: list[OpenAICardStory]
    summary: str


class OpenAIProvider:
    def __init__(
        self,
        *,
        api_key: SecretStr,
        model: str,
        timeout_seconds: float,
        max_retries: int,
        story_max_characters: int,
        summary_max_characters: int,
        client: AsyncOpenAI | None = None,
    ) -> None:
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.story_max_characters = story_max_characters
        self.summary_max_characters = summary_max_characters
        self._client = (
            client
            if client is not None
            else AsyncOpenAI(
                api_key=api_key.get_secret_value(),
                timeout=timeout_seconds,
                max_retries=max_retries,
            )
        )

    async def generate_reading(
        self,
        request: GenerateReadingRequest,
    ) -> GenerateReadingResult:
        input_text = build_tarot_reading_input(
            request,
            story_max_characters=self.story_max_characters,
            summary_max_characters=self.summary_max_characters,
        )
        try:
            response = await self._client.responses.parse(
                model=self.model,
                instructions=TAROT_READING_INSTRUCTIONS,
                input=input_text,
                text_format=OpenAITarotReadingOutput,
                max_output_tokens=self._max_output_tokens(len(request.cards)),
                store=False,
            )
            if response.status == "incomplete":
                self._log_failure("incomplete_response")
                raise InvalidAIProviderResponseError("OpenAI returned an incomplete response")
            if response.status != "completed":
                self._log_failure("unexpected_status")
                raise AIProviderUnavailableError("OpenAI could not complete the request")

            for output in response.output:
                if output.type != "message":
                    continue
                for content in output.content:
                    if content.type == "refusal":
                        self._log_failure("refusal")
                        raise AIProviderRefusalError("OpenAI refused the reading request")

            parsed = response.output_parsed
            if parsed is None:
                self._log_failure("missing_parsed_output")
                raise InvalidAIProviderResponseError("OpenAI returned no structured output")
            return GenerateReadingResult(
                cards=[
                    GeneratedCardStory(card_id=card.card_id, story=card.story)
                    for card in parsed.cards
                ],
                summary=parsed.summary,
            )
        except AIError:
            raise
        except APITimeoutError as error:
            self._log_failure("timeout")
            raise AIProviderTimeoutError("OpenAI request timed out") from error
        except RateLimitError as error:
            self._log_failure("rate_limit")
            raise AIProviderUnavailableError("OpenAI is temporarily unavailable") from error
        except APIConnectionError as error:
            self._log_failure("connection")
            raise AIProviderUnavailableError("OpenAI is temporarily unavailable") from error
        except (
            AuthenticationError,
            PermissionDeniedError,
            BadRequestError,
            NotFoundError,
        ) as error:
            self._log_failure("configuration")
            raise InvalidAIConfigurationError("OpenAI configuration was rejected") from error
        except (APIResponseValidationError, ValidationError) as error:
            self._log_failure("invalid_response")
            raise InvalidAIProviderResponseError("OpenAI returned an invalid response") from error
        except APIStatusError as error:
            self._log_failure("provider_status")
            raise AIProviderUnavailableError("OpenAI is temporarily unavailable") from error
        except Exception as error:
            self._log_failure("unexpected")
            raise AIProviderUnavailableError("OpenAI request failed") from error

    def _max_output_tokens(self, card_count: int) -> int:
        character_budget = card_count * self.story_max_characters + self.summary_max_characters
        return min(MAX_OUTPUT_TOKENS, max(MIN_OUTPUT_TOKENS, character_budget * 2))

    @staticmethod
    def _log_failure(category: str) -> None:
        logger.warning("OpenAI request failed: category=%s", category)
