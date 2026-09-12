from datetime import UTC, datetime, timedelta

import jwt
import pytest
from pydantic import SecretStr
from sqlalchemy.exc import IntegrityError

from loredeck.game.user.repositories.base import NewUser, UniqueIdentifiers, UserProfileUpdate
from loredeck.game.user.services.password import PasswordService
from loredeck.game.user.services.token import TokenService
from loredeck.game.user.usecases.signin import InvalidCredentialsError, SigninUseCase
from loredeck.game.user.usecases.signup import SignupUseCase, UserConflictError
from loredeck.shared.models import UserModel

JWT_SECRET = SecretStr("unit-test-secret-that-is-not-used-in-production-0123456789abcdef")


class FakeUserRepository:
    def __init__(self, user: UserModel | None = None) -> None:
        self.user = user
        self.conflicts: set[str] = set()
        self.new_user: NewUser | None = None
        self.raise_integrity_error = False
        self.committed = False
        self.rolled_back = False

    async def find_by_username(self, username: str) -> UserModel | None:
        return self.user if self.user is not None and self.user.username == username else None

    async def find_by_id(self, user_id: int) -> UserModel | None:
        return self.user if self.user is not None and self.user.id == user_id else None

    async def find_conflicts(
        self,
        identifiers: UniqueIdentifiers,
        *,
        exclude_user_id: int | None = None,
    ) -> set[str]:
        return self.conflicts

    async def create(self, new_user: NewUser) -> UserModel:
        self.new_user = new_user
        if self.raise_integrity_error:
            raise IntegrityError("insert", {}, Exception("unique violation"))
        return make_user(password_hash=new_user.password_hash)

    async def update_profile(self, user: UserModel, update: UserProfileUpdate) -> UserModel:
        return user

    async def commit(self) -> None:
        if self.raise_integrity_error:
            raise IntegrityError("commit", {}, Exception("unique violation"))
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


def make_user(*, password_hash: str, username: str = "username") -> UserModel:
    return UserModel(
        id=1,
        username=username,
        password_hash=password_hash,
        phone_number=None,
        profile_pic=None,
        name=None,
        email=None,
        telegram_id=None,
        created_at=datetime(2026, 9, 12, 12, tzinfo=UTC),
    )


def make_token_service() -> TokenService:
    return TokenService(secret=JWT_SECRET, algorithm="HS256", expire_minutes=30)


@pytest.mark.asyncio
async def test_signup_hashes_password_commits_and_returns_token() -> None:
    repository = FakeUserRepository()
    password_service = PasswordService()
    result = await SignupUseCase(repository, password_service, make_token_service()).execute(
        username=" username ",
        password="strong-password",
        phone_number=None,
        name=None,
        email=None,
    )

    assert repository.new_user is not None
    assert repository.new_user.password_hash != "strong-password"
    assert password_service.verify_password("strong-password", repository.new_user.password_hash)
    assert repository.committed
    assert result.token_type == "bearer"
    assert result.expires_in == 1800
    assert result.user.username == "username"


@pytest.mark.asyncio
@pytest.mark.parametrize("conflict", ["username", "email", "phone_number"])
async def test_signup_rejects_preexisting_conflicts(conflict: str) -> None:
    password_service = PasswordService()
    token_service = make_token_service()
    existing = FakeUserRepository()
    existing.conflicts = {conflict}
    with pytest.raises(UserConflictError):
        await SignupUseCase(existing, password_service, token_service).execute(
            username="username",
            password="strong-password",
            phone_number=None,
            name=None,
            email=None,
        )


@pytest.mark.asyncio
async def test_signup_rolls_back_concurrent_uniqueness_race() -> None:
    racing = FakeUserRepository()
    racing.raise_integrity_error = True
    with pytest.raises(UserConflictError):
        await SignupUseCase(racing, PasswordService(), make_token_service()).execute(
            username="username",
            password="strong-password",
            phone_number=None,
            name=None,
            email=None,
        )
    assert racing.rolled_back


@pytest.mark.asyncio
async def test_signin_returns_valid_minimal_jwt() -> None:
    password_service = PasswordService()
    user = make_user(password_hash=password_service.hash_password("strong-password"))
    result = await SigninUseCase(
        FakeUserRepository(user), password_service, make_token_service()
    ).execute(username=" username ", password="strong-password")

    claims = jwt.decode(  # pyright: ignore[reportUnknownMemberType]
        result.access_token,
        JWT_SECRET.get_secret_value(),
        algorithms=["HS256"],
    )
    assert claims["sub"] == "1"
    assert isinstance(claims["iat"], int)
    assert claims["exp"] > claims["iat"]
    assert set(claims) == {"sub", "iat", "exp"}
    assert "password" not in result.access_token
    assert "strong-password" not in result.access_token


@pytest.mark.asyncio
@pytest.mark.parametrize("stored_hash", [None, "malformed-hash"])
async def test_signin_rejects_unknown_user_and_bad_or_malformed_hash(
    stored_hash: str | None,
) -> None:
    password_service = PasswordService()
    repository = FakeUserRepository(
        None if stored_hash is None else make_user(password_hash=stored_hash)
    )
    with pytest.raises(InvalidCredentialsError):
        await SigninUseCase(repository, password_service, make_token_service()).execute(
            username="username", password="wrong-password"
        )


def test_token_validation_rejects_altered_token_and_wrong_algorithm() -> None:
    service = make_token_service()
    token = service.create_access_token(1).value
    altered = f"{token[:-1]}{'a' if token[-1] != 'a' else 'b'}"
    with pytest.raises(jwt.InvalidTokenError):
        service.decode_access_token(altered)

    wrong_algorithm = jwt.encode(  # pyright: ignore[reportUnknownMemberType]
        {"sub": "1", "iat": datetime.now(UTC), "exp": datetime.now(UTC)},
        JWT_SECRET.get_secret_value(),
        algorithm="HS384",
    )
    with pytest.raises(jwt.InvalidTokenError):
        service.decode_access_token(wrong_algorithm)

    now = datetime.now(UTC)
    expired = jwt.encode(  # pyright: ignore[reportUnknownMemberType]
        {"sub": "1", "iat": now - timedelta(minutes=2), "exp": now - timedelta(minutes=1)},
        JWT_SECRET.get_secret_value(),
        algorithm="HS256",
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        service.decode_access_token(expired)
