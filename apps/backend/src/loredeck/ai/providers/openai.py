import logging
from time import monotonic
from typing import Literal
from urllib.parse import urlsplit

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
        base_url: str,
        api_key: SecretStr,
        model: str,
        timeout_seconds: float,
        max_retries: int,
        story_max_characters: int,
        summary_max_characters: int,
        client: AsyncOpenAI | None = None,
        api_mode: Literal["auto", "responses", "ollama"] = "auto",
    ) -> None:
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.story_max_characters = story_max_characters
        self.summary_max_characters = summary_max_characters
        endpoint = urlsplit(base_url)
        self._use_ollama = api_mode == "ollama" or (
            api_mode == "auto"
            and (
                endpoint.hostname == "ollama"
                or (
                    endpoint.hostname in {"localhost", "127.0.0.1", "::1"}
                    and endpoint.port == 11434
                )
            )
        )
        self._client = (
            client
            if client is not None
            else AsyncOpenAI(
                base_url=base_url,
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
        started = monotonic()
        try:
            if self._use_ollama:
                parsed = await self._parse_ollama(input_text, len(request.cards))
            else:
                parsed = await self._parse_responses(input_text, len(request.cards))
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
            print(50 * "3")
            self._log_failure("timeout", error, started)
            raise AIProviderTimeoutError("OpenAI request timed out") from error
        except RateLimitError as error:
            print(50 * "4")
            self._log_failure("rate_limit", error, started)
            raise AIProviderUnavailableError("OpenAI is temporarily unavailable") from error
        except APIConnectionError as error:
            print(50 * "5")
            print("input_text: ", input_text)
            print("request.cards: ", request.cards)
            # print("parsed: ", parsed)
            print("_use_ollama: ", self._use_ollama)
            print(50 * "5")
            self._log_failure("connection", error, started)
            raise AIProviderUnavailableError("OpenAI is temporarily unavailable") from error
        except (
            AuthenticationError,
            PermissionDeniedError,
            BadRequestError,
            NotFoundError,
        ) as error:
            print(50 * "6")
            self._log_failure("configuration", error, started)
            raise InvalidAIConfigurationError("OpenAI configuration was rejected") from error
        except (APIResponseValidationError, ValidationError) as error:
            print(50 * "7")
            self._log_failure("invalid_response", error, started)
            raise InvalidAIProviderResponseError("OpenAI returned an invalid response") from error
        except APIStatusError as error:
            print(50 * "8")
            self._log_failure("provider_status", error, started)
            raise AIProviderUnavailableError("OpenAI is temporarily unavailable") from error
        except Exception as error:
            print(50 * "9")
            self._log_failure("unexpected", error, started)
            raise AIProviderUnavailableError("OpenAI request failed") from error

    async def _parse_responses(self, input_text: str, card_count: int) -> OpenAITarotReadingOutput:
        response = await self._client.responses.parse(
            model=self.model,
            instructions=TAROT_READING_INSTRUCTIONS,
            input=input_text,
            text_format=OpenAITarotReadingOutput,
            max_output_tokens=self._max_output_tokens(card_count),
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
        return parsed

    async def _parse_ollama(self, input_text: str, card_count: int) -> OpenAITarotReadingOutput:
        print(50*"f")
        print(self._client)
        print(50*"f")
        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": TAROT_READING_INSTRUCTIONS},
                    {"role": "user", "content": input_text},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "tarot_reading",
                        "strict": True,
                        "schema": OpenAITarotReadingOutput.model_json_schema(),
                    },
                },
                max_tokens=self._max_output_tokens(card_count),
                # Ollama maps 'none' to think=false for supported local models.
                reasoning_effort="none",
            )
        except APIConnectionError as error:
            # Diagnostic output for your local Ollama connection.
            print(50*"g")
            print(
                "Ollama connection failed: base_url=%s cause_type=%s cause=%s",
                self._client.base_url,
                type(error.__cause__).__name__,
                str(error.__cause__),
            )
            print(50 * "g")
            raise AIProviderUnavailableError(
                "OpenAI is temporarily unavailable"
            ) from error
        if len(response.choices) != 1:
            print(50*"a")
            self._log_failure("invalid_choices")
            raise InvalidAIProviderResponseError("OpenAI returned an invalid choice count")
        choice = response.choices[0]
        if choice.message.refusal or choice.finish_reason == "content_filter":
            print(50 * "b")
            self._log_failure("refusal")
            raise AIProviderRefusalError("OpenAI refused the reading request")
        if choice.finish_reason != "stop":
            print(50 * "c")
            self._log_failure("incomplete_response")
            raise InvalidAIProviderResponseError("OpenAI returned an incomplete response")
        if not choice.message.content:
            print(50 * "d")
            self._log_failure("missing_parsed_output")
            raise InvalidAIProviderResponseError("OpenAI returned no structured output")
        print(50 * "e")
        return OpenAITarotReadingOutput.model_validate_json(choice.message.content)

    def _max_output_tokens(self, card_count: int) -> int:
        character_budget = card_count * self.story_max_characters + self.summary_max_characters
        return min(MAX_OUTPUT_TOKENS, max(MIN_OUTPUT_TOKENS, character_budget * 2))

    def _log_failure(
        self, category: str, error: Exception | None = None, started: float | None = None
    ) -> None:
        # Never log exception text/body, URLs, headers, model names, or reading content.
        logger.warning(
            "OpenAI request failed: category=%s api=%s upstream_status=%s "
            "exception_type=%s elapsed_seconds=%s timeout_seconds=%s max_retries=%s",
            category,
            "chat.completions" if self._use_ollama else "responses",
            error.status_code if isinstance(error, APIStatusError) else None,
            type(error).__name__ if error is not None else None,
            round(monotonic() - started, 3) if started is not None else None,
            self.timeout_seconds,
            self.max_retries,
        )
