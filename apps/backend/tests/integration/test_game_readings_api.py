from collections.abc import Iterator
from typing import Any, Protocol, cast

import pytest
from starlette.testclient import TestClient

from loredeck.game.dependencies import get_draw_reading_use_case
from loredeck.game.exceptions import (
    DeckNotFoundError,
    InactiveDeckError,
    InsufficientActiveCardsError,
)
from loredeck.game.main import app
from loredeck.game.use_cases import (
    DrawnCard,
    Orientation,
    PublicCard,
    ReadingPosition,
    ReadingResult,
    Spread,
)


class HttpResponse(Protocol):
    status_code: int

    def json(self) -> object: ...


class StubDrawReadingUseCase:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.questions: list[str | None] = []

    async def execute(
        self,
        *,
        deck_id: int,
        spread: Spread,
        question: str | None,
    ) -> ReadingResult:
        self.questions.append(question)
        if self.error is not None:
            raise self.error

        positions = (
            (ReadingPosition.PRESENT,)
            if spread == Spread.ONE_CARD
            else (
                ReadingPosition.PAST,
                ReadingPosition.PRESENT,
                ReadingPosition.FUTURE,
            )
        )
        return ReadingResult(
            cards=tuple(
                DrawnCard(
                    position=position,
                    orientation=Orientation.UPRIGHT,
                    card=PublicCard(
                        title=f"Card {index}",
                        description=None,
                        number=index,
                        image_path=f"cards/{index}.webp",
                    ),
                )
                for index, position in enumerate(positions, start=1)
            )
        )


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_draw_reading_use_case] = lambda: StubDrawReadingUseCase()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("spread", "positions"),
    [("one_card", ["present"]), ("three_card", ["past", "present", "future"])],
)
def test_create_reading_contract(
    client: TestClient,
    spread: str,
    positions: list[str],
) -> None:
    use_case = StubDrawReadingUseCase()
    app.dependency_overrides[get_draw_reading_use_case] = lambda: use_case

    response = cast(
        HttpResponse,
        client.post(  # pyright: ignore[reportUnknownMemberType]
            "/readings",
            json={"deck_id": 1, "spread": spread, "question": "A question"},
        ),
    )

    assert response.status_code == 200
    body = cast(dict[str, Any], response.json())
    assert [card["position"] for card in body["cards"]] == positions
    assert body["summary"] == ""
    assert use_case.questions == ["A question"]
    for drawn_card in body["cards"]:
        assert drawn_card["orientation"] == "upright"
        assert drawn_card["story"] == ""
        assert set(drawn_card["card"]) == {"title", "description", "number", "image_path"}


def test_create_reading_accepts_omitted_question(client: TestClient) -> None:
    use_case = StubDrawReadingUseCase()
    app.dependency_overrides[get_draw_reading_use_case] = lambda: use_case

    response = cast(
        HttpResponse,
        client.post(  # pyright: ignore[reportUnknownMemberType]
            "/readings", json={"deck_id": 1, "spread": "one_card"}
        ),
    )

    assert response.status_code == 200
    assert use_case.questions == [None]


@pytest.mark.parametrize(
    "body",
    [
        {"spread": "one_card"},
        {"deck_id": 0, "spread": "one_card"},
        {"deck_id": 1, "spread": "unsupported"},
    ],
)
def test_create_reading_validates_request(client: TestClient, body: dict[str, object]) -> None:
    response = cast(
        HttpResponse,
        client.post(  # pyright: ignore[reportUnknownMemberType]
            "/readings", json=body
        ),
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("error", "status_code"),
    [
        (DeckNotFoundError(), 404),
        (InactiveDeckError(), 404),
        (InsufficientActiveCardsError(), 409),
    ],
)
def test_create_reading_maps_application_errors(
    client: TestClient,
    error: Exception,
    status_code: int,
) -> None:
    app.dependency_overrides[get_draw_reading_use_case] = lambda: StubDrawReadingUseCase(error)

    response = cast(
        HttpResponse,
        client.post(  # pyright: ignore[reportUnknownMemberType]
            "/readings", json={"deck_id": 1, "spread": "three_card"}
        ),
    )

    assert response.status_code == status_code
