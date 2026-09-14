from loredeck.ai.exceptions import InvalidAIProviderResponseError
from loredeck.ai.providers.base import AIProvider
from loredeck.ai.schemas import GeneratedCardStory, GenerateReadingRequest, GenerateReadingResult


class AIService:
    def __init__(
        self,
        provider: AIProvider,
        *,
        story_max_characters: int,
        summary_max_characters: int,
    ) -> None:
        self._provider = provider
        self._story_max_characters = story_max_characters
        self._summary_max_characters = summary_max_characters

    async def generate_reading(self, request: GenerateReadingRequest) -> GenerateReadingResult:
        if not request.cards:
            raise InvalidAIProviderResponseError("A reading requires at least one input card")

        result = await self._provider.generate_reading(request)
        input_ids = [card.card_id for card in request.cards]
        result_ids = [card.card_id for card in result.cards]

        if len(result_ids) != len(set(result_ids)):
            raise InvalidAIProviderResponseError("Provider returned duplicate card IDs")

        input_id_set = set(input_ids)
        result_id_set = set(result_ids)
        if result_id_set - input_id_set:
            raise InvalidAIProviderResponseError("Provider returned unknown card IDs")
        if input_id_set - result_id_set:
            raise InvalidAIProviderResponseError("Provider omitted input card IDs")
        if len(result_ids) != len(input_ids):
            raise InvalidAIProviderResponseError("Provider returned an invalid card count")

        stories_by_id: dict[int, GeneratedCardStory] = {}
        for card in result.cards:
            story = card.story.strip()
            if not story:
                raise InvalidAIProviderResponseError("Provider returned an empty card story")
            if len(story) > self._story_max_characters:
                raise InvalidAIProviderResponseError("Provider returned an overlong card story")
            stories_by_id[card.card_id] = GeneratedCardStory(card_id=card.card_id, story=story)

        summary = result.summary.strip()
        if not summary:
            raise InvalidAIProviderResponseError("Provider returned an empty summary")
        if len(summary) > self._summary_max_characters:
            raise InvalidAIProviderResponseError("Provider returned an overlong summary")

        return GenerateReadingResult(
            cards=[stories_by_id[card_id] for card_id in input_ids],
            summary=summary,
        )
