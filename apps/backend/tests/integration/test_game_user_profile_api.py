from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol, cast

import jwt
import pytest
from pydantic import SecretStr
from sqlalchemy.exc import IntegrityError
from starlette.testclient import TestClient

from loredeck.game.main import app
from loredeck.game.user.api.router import get_token_service, get_user_repository
from loredeck.game.user.repositories.base import (
    NewUser,
    UniqueIdentifiers,
    UnsetType,
    UserProfileUpdate,
)
from loredeck.game.user.services.token import TokenService
from loredeck.shared.models import UserModel

TEST_SECRET = "profile-test-secret-not-used-in-production-0123456789abcdef"
TOKEN_SERVICE = TokenService(secret=SecretStr(TEST_SECRET), algorithm="HS256", expire_minutes=30)


class HttpResponse(Protocol):
    status_code: int
    headers: dict[str, str]

    def json(self) -> object: ...


def make_user(user_id: int = 1, username: str = "username") -> UserModel:
    return UserModel(
        id=user_id,
        username=username,
        password_hash="not-public",
        phone_number="+49123456789",
        profile_pic="/static/profiles/user.webp",
        name="User Name",
        email="user@example.com",
        telegram_id=None,
        created_at=datetime(2026, 9, 12, 12, tzinfo=UTC),
    )


class FakeUserRepository:
    def __init__(self) -> None:
        self.user = make_user()
        self.conflicts: set[str] = set()
        self.raise_integrity_error = False
        self.committed = False
        self.rolled_back = False

    async def find_by_id(self, user_id: int) -> UserModel | None:
        return self.user if self.user.id == user_id else None

    async def find_by_username(self, username: str) -> UserModel | None:
        return self.user if self.user.username == username else None

    async def find_conflicts(
        self,
        identifiers: UniqueIdentifiers,
        *,
        exclude_user_id: int | None = None,
    ) -> set[str]:
        return self.conflicts

    async def create(self, new_user: NewUser) -> UserModel:
        raise AssertionError("profile tests must not create users")

    async def update_profile(self, user: UserModel, update: UserProfileUpdate) -> UserModel:
        if self.raise_integrity_error:
            raise IntegrityError("update", {}, Exception("unique violation"))
        for field_name in ("username", "phone_number", "profile_pic", "name", "email"):
            value = getattr(update, field_name)
            if not isinstance(value, UnsetType):
                setattr(user, field_name, value)
        return user

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


@pytest.fixture
def repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def client(repository: FakeUserRepository) -> Iterator[TestClient]:
    app.dependency_overrides[get_user_repository] = lambda: repository
    app.dependency_overrides[get_token_service] = lambda: TOKEN_SERVICE
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def authorization(token: str | None = None) -> dict[str, str]:
    return {"Authorization": f"Bearer {token or TOKEN_SERVICE.create_access_token(1).value}"}


def test_get_profile_returns_authenticated_public_user(client: TestClient) -> None:
    response = cast(
        HttpResponse,
        client.get(  # pyright: ignore[reportUnknownMemberType]
            "/users/profile", headers=authorization()
        ),
    )
    assert response.status_code == 200
    body = cast(dict[str, Any], response.json())
    assert body == {
        "id": 1,
        "username": "username",
        "phone_number": "+49123456789",
        "profile_pic": "/static/profiles/user.webp",
        "name": "User Name",
        "email": "user@example.com",
        "telegram_id": None,
        "created_at": "2026-09-12T12:00:00Z",
    }
    assert "password" not in str(body)


@pytest.mark.parametrize(
    "headers",
    [None, {"Authorization": "Bearer invalid-token"}],
    ids=["missing", "invalid"],
)
def test_get_profile_rejects_missing_or_invalid_token(
    client: TestClient, headers: dict[str, str] | None
) -> None:
    response = cast(
        HttpResponse,
        client.get(  # pyright: ignore[reportUnknownMemberType]
            "/users/profile", headers=headers
        ),
    )
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {"detail": "Invalid or missing access token"}


@pytest.mark.parametrize(
    "claims",
    [
        {"iat": datetime.now(UTC), "exp": datetime.now(UTC) + timedelta(minutes=1)},
        {
            "sub": "invalid",
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(minutes=1),
        },
        {"sub": "2", "iat": datetime.now(UTC), "exp": datetime.now(UTC) + timedelta(minutes=1)},
        {
            "sub": "1",
            "iat": datetime.now(UTC) - timedelta(minutes=2),
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
    ],
    ids=["missing-sub", "invalid-sub", "deleted-user", "expired"],
)
def test_get_profile_rejects_invalid_identity_claims(
    client: TestClient, claims: dict[str, object]
) -> None:
    token = jwt.encode(  # pyright: ignore[reportUnknownMemberType]
        claims, TEST_SECRET, algorithm="HS256"
    )
    response = cast(
        HttpResponse,
        client.get(  # pyright: ignore[reportUnknownMemberType]
            "/users/profile", headers=authorization(token)
        ),
    )
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_patch_profile_changes_only_explicit_fields(
    client: TestClient, repository: FakeUserRepository
) -> None:
    response = cast(
        HttpResponse,
        client.patch(  # pyright: ignore[reportUnknownMemberType]
            "/users/profile",
            headers=authorization(),
            json={"username": " new_username ", "name": None},
        ),
    )
    assert response.status_code == 200
    body = cast(dict[str, Any], response.json())
    assert body["username"] == "new_username"
    assert body["name"] is None
    assert body["phone_number"] == "+49123456789"
    assert body["email"] == "user@example.com"
    assert repository.committed


@pytest.mark.parametrize("field", ["phone_number", "profile_pic", "name", "email"])
def test_patch_profile_can_clear_nullable_fields(client: TestClient, field: str) -> None:
    response = cast(
        HttpResponse,
        client.patch(  # pyright: ignore[reportUnknownMemberType]
            "/users/profile", headers=authorization(), json={field: None}
        ),
    )
    assert response.status_code == 200
    assert cast(dict[str, Any], response.json())[field] is None


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"username": None},
        {"username": "   "},
        {"email": "invalid"},
        {"phone_number": "09121234567"},
        {"telegram_id": 2},
        {"password": "new-password"},
        {"password_hash": "hash"},
        {"id": 2},
        {"created_at": "2026-09-12T12:00:00Z"},
    ],
)
def test_patch_profile_rejects_invalid_or_protected_fields(
    client: TestClient, body: dict[str, object]
) -> None:
    response = cast(
        HttpResponse,
        client.patch(  # pyright: ignore[reportUnknownMemberType]
            "/users/profile", headers=authorization(), json=body
        ),
    )
    assert response.status_code == 422


@pytest.mark.parametrize("conflict", ["username", "email", "phone_number"])
def test_patch_profile_maps_identifier_conflicts(
    client: TestClient,
    repository: FakeUserRepository,
    conflict: str,
) -> None:
    repository.conflicts = {conflict}
    response = cast(
        HttpResponse,
        client.patch(  # pyright: ignore[reportUnknownMemberType]
            "/users/profile", headers=authorization(), json={"username": "taken"}
        ),
    )
    assert response.status_code == 409
    assert "constraint" not in str(response.json()).lower()


def test_patch_profile_maps_uniqueness_race(
    client: TestClient, repository: FakeUserRepository
) -> None:
    repository.raise_integrity_error = True
    response = cast(
        HttpResponse,
        client.patch(  # pyright: ignore[reportUnknownMemberType]
            "/users/profile", headers=authorization(), json={"username": "racing"}
        ),
    )
    assert response.status_code == 409
    assert repository.rolled_back


def test_patch_profile_accepts_existing_values_for_current_user(
    client: TestClient, repository: FakeUserRepository
) -> None:
    response = cast(
        HttpResponse,
        client.patch(  # pyright: ignore[reportUnknownMemberType]
            "/users/profile",
            headers=authorization(),
            json={
                "username": repository.user.username,
                "email": repository.user.email,
                "phone_number": repository.user.phone_number,
            },
        ),
    )
    assert response.status_code == 200


def test_openapi_marks_only_profile_routes_as_bearer_authenticated(
    client: TestClient,
) -> None:
    response = cast(
        HttpResponse,
        client.get("/openapi.json"),  # pyright: ignore[reportUnknownMemberType]
    )
    schema = cast(dict[str, Any], response.json())
    paths = cast(dict[str, Any], schema["paths"])
    assert paths["/users/profile"]["get"]["security"] == [{"HTTPBearer": []}]
    assert paths["/users/profile"]["patch"]["security"] == [{"HTTPBearer": []}]
    assert "security" not in paths["/users/signup"]["post"]
    assert "security" not in paths["/users/signin"]["post"]
