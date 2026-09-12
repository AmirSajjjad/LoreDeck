from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any, Protocol, cast

import pytest
from starlette.testclient import TestClient

from loredeck.game.main import app
from loredeck.game.user.api.router import get_signin_use_case, get_signup_use_case
from loredeck.game.user.usecases.signin import InvalidCredentialsError
from loredeck.game.user.usecases.signup import AuthenticationResult, PublicUser, UserConflictError


class HttpResponse(Protocol):
    status_code: int
    headers: dict[str, str]

    def json(self) -> object: ...


def authentication_result() -> AuthenticationResult:
    return AuthenticationResult(
        access_token="signed.jwt.token",
        token_type="bearer",
        expires_in=1800,
        user=PublicUser(
            id=1,
            username="username",
            phone_number=None,
            profile_pic=None,
            name=None,
            email=None,
            telegram_id=None,
            created_at=datetime(2026, 9, 12, 12, tzinfo=UTC),
        ),
    )


class StubUseCase:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    async def execute(self, **values: object) -> AuthenticationResult:
        if self.error is not None:
            raise self.error
        return authentication_result()


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_signup_use_case] = lambda: StubUseCase()
    app.dependency_overrides[get_signin_use_case] = lambda: StubUseCase()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_signup_contract_and_safe_response(client: TestClient) -> None:
    response = cast(
        HttpResponse,
        client.post(  # pyright: ignore[reportUnknownMemberType]
            "/users/signup",
            json={"username": "username", "password": "strong-password"},
        ),
    )
    assert response.status_code == 201
    body = cast(dict[str, Any], response.json())
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 1800
    assert body["user"]["username"] == "username"
    assert "password" not in str(body)


@pytest.mark.parametrize(
    "field",
    ["username", "email", "phone_number"],
)
def test_signup_conflicts_are_safe(client: TestClient, field: str) -> None:
    app.dependency_overrides[get_signup_use_case] = lambda: StubUseCase(UserConflictError())
    response = cast(
        HttpResponse,
        client.post(  # pyright: ignore[reportUnknownMemberType]
            "/users/signup",
            json={"username": "username", "password": "strong-password"},
        ),
    )
    assert response.status_code == 409
    assert field not in str(response.json())


@pytest.mark.parametrize("removed_field", ["profile_pic", "telegram_id"])
def test_signup_rejects_removed_fields(client: TestClient, removed_field: str) -> None:
    response = cast(
        HttpResponse,
        client.post(  # pyright: ignore[reportUnknownMemberType]
            "/users/signup",
            json={
                "username": "username",
                "password": "strong-password",
                removed_field: "value",
            },
        ),
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    "phone_number",
    ["09121234567", "+0123456789", "+1234567", "+1234567890123456", "+98 912 123 4567"],
)
def test_signup_rejects_invalid_phone_numbers(
    client: TestClient,
    phone_number: str,
) -> None:
    response = cast(
        HttpResponse,
        client.post(  # pyright: ignore[reportUnknownMemberType]
            "/users/signup",
            json={
                "username": "username",
                "password": "strong-password",
                "phone_number": phone_number,
            },
        ),
    )
    assert response.status_code == 422


def test_signup_accepts_e164_phone_number(client: TestClient) -> None:
    response = cast(
        HttpResponse,
        client.post(  # pyright: ignore[reportUnknownMemberType]
            "/users/signup",
            json={
                "username": "username",
                "password": "strong-password",
                "phone_number": " +989121234567 ",
            },
        ),
    )
    assert response.status_code == 201


@pytest.mark.parametrize(
    "body",
    [
        {"username": "username", "password": "short"},
        {"username": "username", "password": "strong-password", "email": "invalid"},
    ],
)
def test_signup_validates_request(client: TestClient, body: dict[str, object]) -> None:
    response = cast(
        HttpResponse,
        client.post("/users/signup", json=body),  # pyright: ignore[reportUnknownMemberType]
    )
    assert response.status_code == 422


@pytest.mark.parametrize("error", [InvalidCredentialsError(), InvalidCredentialsError()])
def test_signin_invalid_credentials_are_generic(client: TestClient, error: Exception) -> None:
    app.dependency_overrides[get_signin_use_case] = lambda: StubUseCase(error)
    response = cast(
        HttpResponse,
        client.post(  # pyright: ignore[reportUnknownMemberType]
            "/users/signin", json={"username": "username", "password": "wrong"}
        ),
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_signin_success(client: TestClient) -> None:
    response = cast(
        HttpResponse,
        client.post(  # pyright: ignore[reportUnknownMemberType]
            "/users/signin",
            json={"username": "username", "password": "strong-password"},
        ),
    )
    assert response.status_code == 200
    assert cast(dict[str, object], response.json())["access_token"] == "signed.jwt.token"
