from collections.abc import Iterator, Sequence
from datetime import UTC, datetime
from typing import Any, Protocol, cast

import pytest
from starlette.testclient import TestClient

from loredeck.game.main import app
from loredeck.game.readings.api.router import (
    get_list_reading_history_use_case,
    get_reading_history_use_case,
)
from loredeck.game.readings.usecases.create_reading import (
    Orientation,
    PublicCard,
    ReadingPosition,
    Spread,
)
from loredeck.game.readings.usecases.history import (
    HistoricalCard,
    HistoryDeck,
    HistoryDetail,
    HistoryListItem,
    HistoryListResult,
    HistoryNotFoundError,
)
from loredeck.game.user.api.router import get_current_user
from loredeck.shared.models import UserModel


class HttpResponse(Protocol):
    status_code: int

    def json(self) -> object: ...


class StubListHistory:
    def __init__(self, items: Sequence[HistoryListItem] = ()) -> None:
        self.items = items
        self.calls: list[tuple[int, int, int]] = []

    async def execute(self, user_id: int, *, limit: int, offset: int) -> HistoryListResult:
        self.calls.append((user_id, limit, offset))
        return HistoryListResult(
            items=self.items, total=len(self.items), limit=limit, offset=offset
        )


class StubGetHistory:
    def __init__(self, value: HistoryDetail | None = None) -> None:
        self.value = value

    async def execute(self, user_id: int, history_id: int) -> HistoryDetail:
        if self.value is None:
            raise HistoryNotFoundError
        return self.value


def current_user() -> UserModel:
    return UserModel(id=7, username="reader", password_hash="hash", created_at=datetime.now(UTC))


def make_item(identifier: int) -> HistoryListItem:
    return HistoryListItem(
        id=identifier,
        created_at=datetime(2026, 9, 13, tzinfo=UTC),
        question=None,
        deck=HistoryDeck(id=2, title="Major Arcana"),
        spread=Spread.ONE_CARD,
    )


def make_detail(spread: Spread) -> HistoryDetail:
    positions = (
        (ReadingPosition.PRESENT,)
        if spread == Spread.ONE_CARD
        else (ReadingPosition.PAST, ReadingPosition.PRESENT, ReadingPosition.FUTURE)
    )
    cards = tuple(
        HistoricalCard(
            position=position,
            orientation=Orientation.UPRIGHT,
            card=PublicCard(title=f"Card {index}", description=None, number=None, image_path=None),
            story=None,
        )
        for index, position in enumerate(positions, 1)
    )
    return HistoryDetail(
        id=3,
        created_at=datetime(2026, 9, 13, tzinfo=UTC),
        question=None,
        deck=HistoryDeck(id=2, title="Major Arcana"),
        spread=spread,
        cards=cards,
        summary=None,
    )


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_list_reading_history_use_case] = StubListHistory
    app.dependency_overrides[get_reading_history_use_case] = StubGetHistory
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def authenticate() -> None:
    app.dependency_overrides[get_current_user] = current_user


@pytest.mark.parametrize("path", ["/readings/history", "/readings/history/1"])
def test_history_requires_authentication(client: TestClient, path: str) -> None:
    response = cast(HttpResponse, client.get(path))  # pyright: ignore[reportUnknownMemberType]
    assert response.status_code == 401


def test_history_list_contract_and_pagination(client: TestClient) -> None:
    authenticate()
    use_case = StubListHistory([make_item(2), make_item(1)])
    app.dependency_overrides[get_list_reading_history_use_case] = lambda: use_case
    response = cast(HttpResponse, client.get("/readings/history?limit=10&offset=20"))  # pyright: ignore[reportUnknownMemberType]
    body = cast(dict[str, Any], response.json())
    assert response.status_code == 200
    assert (body["total"], body["limit"], body["offset"]) == (2, 10, 20)
    assert [item["id"] for item in body["items"]] == [2, 1]
    assert set(body["items"][0]) == {"id", "created_at", "question", "deck", "spread"}
    assert use_case.calls == [(7, 10, 20)]


def test_empty_history_returns_success(client: TestClient) -> None:
    authenticate()
    response = cast(HttpResponse, client.get("/readings/history"))  # pyright: ignore[reportUnknownMemberType]
    assert response.status_code == 200
    assert cast(dict[str, Any], response.json())["items"] == []


@pytest.mark.parametrize("query", ["limit=0", "limit=101", "offset=-1"])
def test_history_validates_pagination(client: TestClient, query: str) -> None:
    authenticate()
    response = cast(HttpResponse, client.get(f"/readings/history?{query}"))  # pyright: ignore[reportUnknownMemberType]
    assert response.status_code == 422


@pytest.mark.parametrize("spread", [Spread.ONE_CARD, Spread.THREE_CARD])
def test_history_detail_reconstructs_cards(client: TestClient, spread: Spread) -> None:
    authenticate()
    app.dependency_overrides[get_reading_history_use_case] = lambda: StubGetHistory(
        make_detail(spread)
    )
    response = cast(HttpResponse, client.get("/readings/history/3"))  # pyright: ignore[reportUnknownMemberType]
    body = cast(dict[str, Any], response.json())
    expected = ["present"] if spread == Spread.ONE_CARD else ["past", "present", "future"]
    assert response.status_code == 200
    assert [card["position"] for card in body["cards"]] == expected
    assert all(card["orientation"] == "upright" for card in body["cards"])
    assert body["question"] is None and body["summary"] is None
    assert set(body) == {"id", "created_at", "question", "deck", "spread", "cards", "summary"}


def test_missing_or_foreign_history_is_not_disclosed(client: TestClient) -> None:
    authenticate()
    response = cast(HttpResponse, client.get("/readings/history/99"))  # pyright: ignore[reportUnknownMemberType]
    assert response.status_code == 404


def test_history_routes_are_bearer_protected_in_openapi(client: TestClient) -> None:
    response = cast(HttpResponse, client.get("/openapi.json"))  # pyright: ignore[reportUnknownMemberType]
    schema = cast(dict[str, Any], response.json())
    assert schema["paths"]["/readings/history"]["get"]["security"] == [{"HTTPBearer": []}]
    assert schema["paths"]["/readings/history/{history_id}"]["get"]["security"] == [
        {"HTTPBearer": []}
    ]
