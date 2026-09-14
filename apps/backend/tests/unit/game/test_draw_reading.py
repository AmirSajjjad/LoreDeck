from collections.abc import Sequence

import pytest
from pytest import MonkeyPatch

from loredeck.ai.exceptions import AIProviderUnavailableError, InvalidAIProviderResponseError
from loredeck.ai.schemas import (
    GeneratedCardStory,
    GenerateReadingRequest,
    GenerateReadingResult,
)
from loredeck.ai.service import AIReadingService, AIService
from loredeck.game.readings.repositories.base import NewReadingHistory
from loredeck.game.readings.usecases import create_reading
from loredeck.game.readings.usecases.create_reading import (
    DeckNotFoundError,
    DrawReadingUseCase,
    InactiveDeckError,
    InsufficientActiveCardsError,
    ReadingGenerationError,
    ReadingPersistenceError,
    ReadingPosition,
    Spread,
)
from loredeck.shared.models import CardModel


class FakeReadingRepository:
    def __init__(
        self,
        *,
        deck_is_active: bool | None,
        active_cards: Sequence[CardModel] = (),
    ) -> None:
        self.deck_is_active = deck_is_active
        self.active_cards = active_cards
        self.requested_card_ids: Sequence[int] = ()
        self.histories: list[NewReadingHistory] = []
        self.pending_history: NewReadingHistory | None = None
        self.commit_count = 0
        self.rollback_count = 0
        self.selection_release_count = 0
        self.fail_history = False
        self.fail_commit = False

    async def get_deck_active_status(self, deck_id: int) -> bool | None:
        return self.deck_is_active

    async def list_active_card_ids(self, deck_id: int) -> Sequence[int]:
        return [card.id for card in self.active_cards if card.deck_id == deck_id and card.is_active]

    async def get_active_cards_by_ids(
        self,
        deck_id: int,
        card_ids: Sequence[int],
    ) -> Sequence[CardModel]:
        self.requested_card_ids = card_ids
        return [
            card
            for card in self.active_cards
            if card.id in card_ids and card.deck_id == deck_id and card.is_active
        ]

    async def add_history(self, history: NewReadingHistory) -> None:
        if self.fail_history:
            raise RuntimeError("database unavailable")
        self.pending_history = history

    async def release_selection_transaction(self) -> None:
        self.selection_release_count += 1

    async def commit(self) -> None:
        if self.fail_commit:
            raise RuntimeError("commit failed")
        self.commit_count += 1
        assert self.pending_history is not None
        self.histories.append(self.pending_history)
        self.pending_history = None

    async def rollback(self) -> None:
        self.rollback_count += 1
        self.pending_history = None


class FixedSystemRandom:
    def sample(self, population: Sequence[int], k: int) -> list[int]:
        return list(reversed(population))[:k]


class FakeAIService:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.requests: list[GenerateReadingRequest] = []

    async def generate_reading(self, request: GenerateReadingRequest) -> GenerateReadingResult:
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return GenerateReadingResult(
            cards=[
                GeneratedCardStory(card_id=card.card_id, story=f"Story {card.card_id}")
                for card in reversed(request.cards)
            ],
            summary="Generated summary",
        )


class StaticAIProvider:
    def __init__(self, result: GenerateReadingResult) -> None:
        self.result = result

    async def generate_reading(self, request: GenerateReadingRequest) -> GenerateReadingResult:
        del request
        return self.result


def make_use_case(
    repository: FakeReadingRepository,
    ai_service: AIReadingService | None = None,
) -> DrawReadingUseCase:
    return DrawReadingUseCase(repository, ai_service or FakeAIService())


def make_card(card_id: int, *, deck_id: int = 1, is_active: bool = True) -> CardModel:
    return CardModel(
        id=card_id,
        deck_id=deck_id,
        title=f"Card {card_id}",
        description=f"Description {card_id}",
        number=card_id,
        image_path=f"cards/{card_id}.webp",
        attributes={},
        is_active=is_active,
    )


@pytest.fixture
def fixed_random(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(create_reading.secrets, "SystemRandom", FixedSystemRandom)


@pytest.mark.asyncio
async def test_one_card_reading_uses_present_position(fixed_random: None) -> None:
    repository = FakeReadingRepository(deck_is_active=True, active_cards=[make_card(1)])

    ai_service = FakeAIService()
    result = await make_use_case(repository, ai_service).execute(
        deck_id=1,
        spread=Spread.ONE_CARD,
        question=None,
    )

    assert len(result.cards) == 1
    assert result.cards[0].position == "present"
    assert result.cards[0].orientation == "upright"
    assert result.cards[0].story == "Story 1"
    assert result.summary == "Generated summary"
    assert len(ai_service.requests) == 1
    assert ai_service.requests[0].question is None
    assert ai_service.requests[0].spread == Spread.ONE_CARD
    assert ai_service.requests[0].cards[0].position == ReadingPosition.PRESENT
    assert ai_service.requests[0].cards[0].orientation == "upright"
    assert repository.histories == []
    assert repository.commit_count == 0


@pytest.mark.asyncio
async def test_three_card_reading_preserves_secure_selection_order(fixed_random: None) -> None:
    repository = FakeReadingRepository(
        deck_is_active=True,
        active_cards=[
            make_card(1),
            make_card(2),
            make_card(3),
            make_card(4, deck_id=2),
            make_card(5, is_active=False),
        ],
    )

    ai_service = FakeAIService()
    result = await make_use_case(repository, ai_service).execute(
        deck_id=1,
        spread=Spread.THREE_CARD,
        question="What should I know?",
    )

    assert repository.requested_card_ids == [3, 2, 1]
    assert [card.position for card in result.cards] == ["past", "present", "future"]
    assert [card.card.number for card in result.cards] == [3, 2, 1]
    assert len({card.card.number for card in result.cards}) == 3
    assert all(card.orientation == "upright" for card in result.cards)
    assert [card.story for card in result.cards] == ["Story 3", "Story 2", "Story 1"]
    assert result.summary == "Generated summary"
    assert len(ai_service.requests) == 1
    ai_request = ai_service.requests[0]
    assert ai_request.question == "What should I know?"
    assert ai_request.spread == Spread.THREE_CARD
    assert [card.card_id for card in ai_request.cards] == [3, 2, 1]
    assert [card.position for card in ai_request.cards] == ["past", "present", "future"]
    assert all(card.orientation == "upright" for card in ai_request.cards)
    assert [card.attributes for card in ai_request.cards] == [{}, {}, {}]
    assert repository.histories == []
    assert repository.commit_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("spread", "expected_ids"),
    [
        (Spread.ONE_CARD, (3, None, None)),
        (Spread.THREE_CARD, (3, 2, 1)),
    ],
)
async def test_authenticated_reading_saves_selected_cards_in_response_order(
    fixed_random: None,
    spread: Spread,
    expected_ids: tuple[int, int | None, int | None],
) -> None:
    repository = FakeReadingRepository(
        deck_is_active=True,
        active_cards=[make_card(1), make_card(2), make_card(3)],
    )

    result = await make_use_case(repository).execute(
        deck_id=1,
        spread=spread,
        question="What should I know?",
        user_id=42,
    )

    assert len(repository.histories) == 1
    history = repository.histories[0]
    assert history.user_id == 42
    assert history.deck_id == 1
    assert history.question == "What should I know?"
    assert (history.first_card_id, history.second_card_id, history.third_card_id) == expected_ids
    expected_stories = tuple(card.story for card in result.cards)
    assert history.first_story == expected_stories[0]
    assert history.second_story == (expected_stories[1] if len(expected_stories) > 1 else None)
    assert history.third_story == (expected_stories[2] if len(expected_stories) > 2 else None)
    assert history.summary == result.summary
    assert repository.commit_count == 1


@pytest.mark.asyncio
async def test_authenticated_reading_stores_missing_question_as_null(
    fixed_random: None,
) -> None:
    repository = FakeReadingRepository(deck_is_active=True, active_cards=[make_card(1)])

    await make_use_case(repository).execute(
        deck_id=1,
        spread=Spread.ONE_CARD,
        question=None,
        user_id=42,
    )

    assert repository.histories[0].question is None


@pytest.mark.asyncio
async def test_ai_failure_creates_no_history(fixed_random: None) -> None:
    repository = FakeReadingRepository(deck_is_active=True, active_cards=[make_card(1)])
    ai_service = FakeAIService(AIProviderUnavailableError("provider detail"))

    with pytest.raises(ReadingGenerationError):
        await make_use_case(repository, ai_service).execute(
            deck_id=1,
            spread=Spread.ONE_CARD,
            question=None,
            user_id=42,
        )

    assert repository.selection_release_count == 1
    assert repository.histories == []
    assert repository.commit_count == 0


@pytest.mark.parametrize(
    "generated_cards",
    [
        [GeneratedCardStory(card_id=3, story="three"), GeneratedCardStory(card_id=2, story="two")],
        [
            GeneratedCardStory(card_id=3, story="three"),
            GeneratedCardStory(card_id=3, story="duplicate"),
            GeneratedCardStory(card_id=2, story="two"),
        ],
        [
            GeneratedCardStory(card_id=3, story="three"),
            GeneratedCardStory(card_id=2, story="two"),
            GeneratedCardStory(card_id=99, story="unknown"),
        ],
    ],
    ids=["missing", "duplicate", "unknown"],
)
@pytest.mark.asyncio
async def test_invalid_ai_card_ids_create_no_history(
    fixed_random: None,
    generated_cards: list[GeneratedCardStory],
) -> None:
    repository = FakeReadingRepository(
        deck_is_active=True,
        active_cards=[make_card(1), make_card(2), make_card(3)],
    )
    ai_service = AIService(
        StaticAIProvider(GenerateReadingResult(cards=generated_cards, summary="Generated summary")),
        story_max_characters=350,
        summary_max_characters=700,
    )

    with pytest.raises(ReadingGenerationError) as caught:
        await make_use_case(repository, ai_service).execute(
            deck_id=1,
            spread=Spread.THREE_CARD,
            question=None,
            user_id=42,
        )

    assert isinstance(caught.value.__cause__, InvalidAIProviderResponseError)
    assert repository.histories == []
    assert repository.commit_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("failure_stage", ["add", "commit"])
async def test_history_persistence_failure_rolls_back_without_partial_history(
    fixed_random: None,
    failure_stage: str,
) -> None:
    repository = FakeReadingRepository(deck_is_active=True, active_cards=[make_card(1)])
    repository.fail_history = failure_stage == "add"
    repository.fail_commit = failure_stage == "commit"

    with pytest.raises(ReadingPersistenceError):
        await make_use_case(repository).execute(
            deck_id=1,
            spread=Spread.ONE_CARD,
            question=None,
            user_id=42,
        )

    assert repository.histories == []
    assert repository.commit_count == 0
    assert repository.rollback_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("deck_is_active", "cards", "expected_error"),
    [
        (None, (), DeckNotFoundError),
        (False, (), InactiveDeckError),
        (True, (make_card(1), make_card(2)), InsufficientActiveCardsError),
    ],
)
async def test_reading_rejects_unavailable_decks_or_cards(
    deck_is_active: bool | None,
    cards: Sequence[CardModel],
    expected_error: type[Exception],
) -> None:
    repository = FakeReadingRepository(deck_is_active=deck_is_active, active_cards=cards)

    with pytest.raises(expected_error):
        await make_use_case(repository).execute(
            deck_id=1,
            spread=Spread.THREE_CARD,
            question=None,
            user_id=42,
        )
    assert repository.histories == []
    assert repository.commit_count == 0
