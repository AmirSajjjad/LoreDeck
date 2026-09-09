from collections.abc import Sequence

import pytest
from pytest import MonkeyPatch

from loredeck.game import use_cases
from loredeck.game.exceptions import (
    DeckNotFoundError,
    InactiveDeckError,
    InsufficientActiveCardsError,
)
from loredeck.game.use_cases import DrawReadingUseCase, Spread
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


class FixedSystemRandom:
    def sample(self, population: Sequence[int], k: int) -> list[int]:
        return list(reversed(population))[:k]


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
    monkeypatch.setattr(use_cases.secrets, "SystemRandom", FixedSystemRandom)


@pytest.mark.asyncio
async def test_one_card_reading_uses_present_position(fixed_random: None) -> None:
    repository = FakeReadingRepository(deck_is_active=True, active_cards=[make_card(1)])

    result = await DrawReadingUseCase(repository).execute(
        deck_id=1,
        spread=Spread.ONE_CARD,
        question=None,
    )

    assert len(result.cards) == 1
    assert result.cards[0].position == "present"
    assert result.cards[0].orientation == "upright"
    assert result.cards[0].story == ""
    assert result.summary == ""


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

    result = await DrawReadingUseCase(repository).execute(
        deck_id=1,
        spread=Spread.THREE_CARD,
        question="What should I know?",
    )

    assert repository.requested_card_ids == [3, 2, 1]
    assert [card.position for card in result.cards] == ["past", "present", "future"]
    assert [card.card.number for card in result.cards] == [3, 2, 1]
    assert len({card.card.number for card in result.cards}) == 3
    assert all(card.orientation == "upright" for card in result.cards)
    assert all(card.story == "" for card in result.cards)


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
        await DrawReadingUseCase(repository).execute(
            deck_id=1,
            spread=Spread.THREE_CARD,
            question=None,
        )
