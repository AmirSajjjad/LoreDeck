from dataclasses import dataclass

import pytest

from loredeck.ai.exceptions import InvalidAIProviderResponseError
from loredeck.ai.schemas import (
    AICardInput,
    GeneratedCardStory,
    GenerateReadingRequest,
    GenerateReadingResult,
)
from loredeck.ai.service import AIService
from loredeck.shared.readings import CardOrientation, ReadingPosition, ReadingSpread


@dataclass
class FakeProvider:
    result: GenerateReadingResult

    async def generate_reading(self, request: GenerateReadingRequest) -> GenerateReadingResult:
        del request
        return self.result


def make_request() -> GenerateReadingRequest:
    return GenerateReadingRequest(
        question="What should I know?",
        spread=ReadingSpread.THREE_CARD,
        cards=[
            AICardInput(
                card_id=card_id,
                position=position,
                orientation=CardOrientation.UPRIGHT,
                title=f"Card {card_id}",
                description="Description",
                attributes={"number": card_id},
            )
            for card_id, position in zip(
                (1, 2, 3),
                (ReadingPosition.PAST, ReadingPosition.PRESENT, ReadingPosition.FUTURE),
                strict=True,
            )
        ],
    )


def make_service(result: GenerateReadingResult, *, story_limit: int = 20, summary_limit: int = 30):
    return AIService(
        FakeProvider(result),
        story_max_characters=story_limit,
        summary_max_characters=summary_limit,
    )


@pytest.mark.asyncio
async def test_service_validates_normalizes_and_preserves_input_order() -> None:
    service = make_service(
        GenerateReadingResult(
            cards=[
                GeneratedCardStory(card_id=3, story=" third "),
                GeneratedCardStory(card_id=1, story=" first "),
                GeneratedCardStory(card_id=2, story=" second "),
            ],
            summary=" summary ",
        )
    )

    result = await service.generate_reading(make_request())

    assert [(card.card_id, card.story) for card in result.cards] == [
        (1, "first"),
        (2, "second"),
        (3, "third"),
    ]
    assert result.summary == "summary"


@pytest.mark.parametrize(
    "cards",
    [
        [GeneratedCardStory(card_id=1, story="one"), GeneratedCardStory(card_id=2, story="two")],
        [
            GeneratedCardStory(card_id=1, story="one"),
            GeneratedCardStory(card_id=1, story="again"),
            GeneratedCardStory(card_id=2, story="two"),
        ],
        [
            GeneratedCardStory(card_id=1, story="one"),
            GeneratedCardStory(card_id=2, story="two"),
            GeneratedCardStory(card_id=99, story="unknown"),
        ],
    ],
    ids=["missing", "duplicate", "unknown"],
)
@pytest.mark.asyncio
async def test_service_rejects_invalid_result_card_ids(cards: list[GeneratedCardStory]) -> None:
    service = make_service(GenerateReadingResult(cards=cards, summary="summary"))

    with pytest.raises(InvalidAIProviderResponseError):
        await service.generate_reading(make_request())


@pytest.mark.parametrize(
    "result",
    [
        GenerateReadingResult(
            cards=[
                GeneratedCardStory(card_id=1, story=" "),
                GeneratedCardStory(card_id=2, story="two"),
                GeneratedCardStory(card_id=3, story="three"),
            ],
            summary="summary",
        ),
        GenerateReadingResult(
            cards=[
                GeneratedCardStory(card_id=1, story="one"),
                GeneratedCardStory(card_id=2, story="two"),
                GeneratedCardStory(card_id=3, story="three"),
            ],
            summary=" \n ",
        ),
    ],
    ids=["empty-story", "empty-summary"],
)
@pytest.mark.asyncio
async def test_service_rejects_empty_content(result: GenerateReadingResult) -> None:
    with pytest.raises(InvalidAIProviderResponseError):
        await make_service(result).generate_reading(make_request())


@pytest.mark.parametrize(("story", "summary"), [("ééé", "ok"), ("ok", "🔮🔮🔮")])
@pytest.mark.asyncio
async def test_service_enforces_unicode_character_limits(story: str, summary: str) -> None:
    result = GenerateReadingResult(
        cards=[
            GeneratedCardStory(card_id=1, story=story),
            GeneratedCardStory(card_id=2, story="ok"),
            GeneratedCardStory(card_id=3, story="ok"),
        ],
        summary=summary,
    )

    with pytest.raises(InvalidAIProviderResponseError):
        await make_service(result, story_limit=2, summary_limit=2).generate_reading(make_request())


@pytest.mark.asyncio
async def test_service_rejects_empty_input_cards_before_calling_provider() -> None:
    request = GenerateReadingRequest(question=None, spread=ReadingSpread.ONE_CARD, cards=[])
    result = GenerateReadingResult(cards=[], summary="summary")

    with pytest.raises(InvalidAIProviderResponseError):
        await make_service(result).generate_reading(request)
