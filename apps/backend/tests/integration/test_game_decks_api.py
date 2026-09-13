from collections.abc import Iterator, Sequence
from typing import Any, Protocol, cast

import pytest
from starlette.testclient import TestClient

from loredeck.game.decks.api.router import get_list_active_decks_use_case
from loredeck.game.decks.repositories.base import DeckSummary
from loredeck.game.main import app


class HttpResponse(Protocol):
    status_code: int

    def json(self) -> object: ...


class StubListActiveDecksUseCase:
    def __init__(self, decks: Sequence[DeckSummary]) -> None:
        self._decks = decks

    async def execute(self) -> Sequence[DeckSummary]:
        return self._decks


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_list_active_decks_use_case] = lambda: StubListActiveDecksUseCase(
        [DeckSummary(id=1, title="Rider-Waite")]
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_decks_are_public_and_return_exact_fields(client: TestClient) -> None:
    response = cast(
        HttpResponse,
        client.get("/decks"),  # pyright: ignore[reportUnknownMemberType]
    )

    assert response.status_code == 200
    body = cast(list[dict[str, Any]], response.json())
    assert body == [{"id": 1, "title": "Rider-Waite"}]
    assert set(body[0]) == {"id", "title"}


def test_decks_return_empty_array_when_none_are_active(client: TestClient) -> None:
    app.dependency_overrides[get_list_active_decks_use_case] = lambda: StubListActiveDecksUseCase(
        []
    )

    response = cast(
        HttpResponse,
        client.get("/decks"),  # pyright: ignore[reportUnknownMemberType]
    )

    assert response.status_code == 200
    assert response.json() == []


def test_decks_are_documented_in_openapi(client: TestClient) -> None:
    response = cast(
        HttpResponse,
        client.get("/openapi.json"),  # pyright: ignore[reportUnknownMemberType]
    )

    schema = cast(dict[str, Any], response.json())
    operation = schema["paths"]["/decks"]["get"]
    assert "security" not in operation
    response_schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert response_schema["items"]["$ref"] == "#/components/schemas/PublicDeckResponse"
