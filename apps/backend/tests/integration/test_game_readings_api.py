from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol, cast

import jwt
import pytest
from pydantic import SecretStr
from starlette.testclient import TestClient

from loredeck.game.main import app
from loredeck.game.readings.api.router import get_draw_reading_use_case
from loredeck.game.readings.usecases.create_reading import (
    DeckNotFoundError,
    DrawnCard,
    InactiveDeckError,
    InsufficientActiveCardsError,
    Orientation,
    PublicCard,
    ReadingGenerationError,
    ReadingPersistenceError,
    ReadingPosition,
    ReadingResult,
    Spread,
)
from loredeck.game.user.api.router import (
    get_optional_current_user,
    get_token_service,
    get_user_repository,
)
from loredeck.game.user.services.token import TokenService
from loredeck.shared.models import UserModel

TEST_SECRET = "readings-test-secret-not-used-in-production-0123456789abcdef"
TOKEN_SERVICE = TokenService(secret=SecretStr(TEST_SECRET), algorithm="HS256", expire_minutes=30)


class HttpResponse(Protocol):
    status_code: int
    headers: dict[str, str]

    def json(self) -> object: ...


class StubDrawReadingUseCase:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.questions: list[str | None] = []
        self.user_ids: list[int | None] = []

    async def execute(
        self,
        *,
        deck_id: int,
        spread: Spread,
        question: str | None,
        user_id: int | None = None,
    ) -> ReadingResult:
        self.questions.append(question)
        self.user_ids.append(user_id)
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
                    story=f"داستان {index}",
                )
                for index, position in enumerate(positions, start=1)
            ),
            summary="جمع‌بندی",
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
    assert body["summary"] == "جمع‌بندی"
    assert use_case.questions == ["A question"]
    assert use_case.user_ids == [None]
    for drawn_card in body["cards"]:
        assert drawn_card["orientation"] == "upright"
        assert drawn_card["story"].startswith("داستان")
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


def test_authenticated_reading_passes_verified_user_to_use_case(client: TestClient) -> None:
    use_case = StubDrawReadingUseCase()
    user = UserModel(
        id=42,
        username="reader",
        password_hash="not-public",
        phone_number=None,
        profile_pic=None,
        name=None,
        email=None,
        telegram_id=None,
        created_at=datetime(2026, 9, 12, 12, tzinfo=UTC),
    )
    app.dependency_overrides[get_draw_reading_use_case] = lambda: use_case
    app.dependency_overrides[get_optional_current_user] = lambda: user

    response = cast(
        HttpResponse,
        client.post(  # pyright: ignore[reportUnknownMemberType]
            "/readings",
            json={"deck_id": 1, "spread": "one_card", "question": "Question"},
        ),
    )

    assert response.status_code == 200
    assert use_case.user_ids == [42]
    assert "history" not in cast(dict[str, Any], response.json())


class FindUserRepository:
    async def find_by_id(self, user_id: int) -> UserModel | None:
        return None


class ExistingUserRepository:
    def __init__(self, user: UserModel) -> None:
        self.user = user

    async def find_by_id(self, user_id: int) -> UserModel | None:
        return self.user if user_id == self.user.id else None


def test_reading_accepts_valid_supplied_token(client: TestClient) -> None:
    use_case = StubDrawReadingUseCase()
    user = UserModel(
        id=42,
        username="reader",
        password_hash="not-public",
        created_at=datetime(2026, 9, 12, 12, tzinfo=UTC),
    )
    app.dependency_overrides[get_draw_reading_use_case] = lambda: use_case
    app.dependency_overrides[get_token_service] = lambda: TOKEN_SERVICE
    app.dependency_overrides[get_user_repository] = lambda: ExistingUserRepository(user)
    token = TOKEN_SERVICE.create_access_token(user.id)

    response = cast(
        HttpResponse,
        client.post(  # pyright: ignore[reportUnknownMemberType]
            "/readings",
            headers={"Authorization": f"Bearer {token.value}"},
            json={"deck_id": 1, "spread": "one_card"},
        ),
    )

    assert response.status_code == 200
    assert use_case.user_ids == [42]


@pytest.mark.parametrize("expired", [False, True], ids=["invalid", "expired"])
def test_reading_rejects_invalid_supplied_token(
    client: TestClient,
    expired: bool,
) -> None:
    use_case = StubDrawReadingUseCase()
    app.dependency_overrides[get_draw_reading_use_case] = lambda: use_case
    app.dependency_overrides[get_token_service] = lambda: TOKEN_SERVICE
    app.dependency_overrides[get_user_repository] = FindUserRepository
    if expired:
        now = datetime.now(UTC)
        token = jwt.encode(  # pyright: ignore[reportUnknownMemberType]
            {
                "sub": "1",
                "iat": now - timedelta(minutes=2),
                "exp": now - timedelta(minutes=1),
            },
            TEST_SECRET,
            algorithm="HS256",
        )
    else:
        token = "invalid-token"

    response = cast(
        HttpResponse,
        client.post(  # pyright: ignore[reportUnknownMemberType]
            "/readings",
            headers={"Authorization": f"Bearer {token}"},
            json={"deck_id": 1, "spread": "one_card"},
        ),
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert use_case.user_ids == []


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
        (ReadingGenerationError(), 503),
        (ReadingPersistenceError(), 500),
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


def test_openapi_documents_reading_bearer_as_optional(client: TestClient) -> None:
    response = cast(
        HttpResponse,
        client.get("/openapi.json"),  # pyright: ignore[reportUnknownMemberType]
    )
    schema = cast(dict[str, Any], response.json())

    assert schema["paths"]["/readings"]["post"]["security"] == [
        {"HTTPBearer": []},
        {},
    ]
