from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from loredeck.game.user.repositories.base import NewUser, UniqueIdentifiers, UserRepository
from loredeck.game.user.services.password import PasswordService
from loredeck.game.user.services.token import TokenService
from loredeck.shared.models import UserModel


class UserConflictError(Exception):
    """Raised when supplied signup identifiers are already registered."""


@dataclass(frozen=True)
class PublicUser:
    id: int
    username: str
    phone_number: str | None
    profile_pic: str | None
    name: str | None
    email: str | None
    telegram_id: int | None
    created_at: datetime


@dataclass(frozen=True)
class AuthenticationResult:
    access_token: str
    token_type: str
    expires_in: int
    user: PublicUser


def to_public_user(user: UserModel) -> PublicUser:
    return PublicUser(
        id=user.id,
        username=user.username,
        phone_number=user.phone_number,
        profile_pic=user.profile_pic,
        name=user.name,
        email=user.email,
        telegram_id=user.telegram_id,
        created_at=user.created_at,
    )


class SignupUseCase:
    def __init__(
        self,
        repository: UserRepository,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:
        self._repository = repository
        self._password_service = password_service
        self._token_service = token_service

    async def execute(
        self,
        *,
        username: str,
        password: str,
        phone_number: str | None,
        name: str | None,
        email: str | None,
    ) -> AuthenticationResult:
        normalized_username = username.strip()
        normalized_email = email.strip().lower() if email is not None else None
        identifiers = UniqueIdentifiers(
            username=normalized_username,
            email=normalized_email,
            phone_number=phone_number,
        )
        if await self._repository.find_conflicts(identifiers):
            raise UserConflictError

        password_hash = self._password_service.hash_password(password)
        try:
            user = await self._repository.create(
                NewUser(
                    username=normalized_username,
                    password_hash=password_hash,
                    phone_number=phone_number,
                    profile_pic=None,
                    name=name,
                    email=normalized_email,
                    telegram_id=None,
                )
            )
            await self._repository.commit()
        except IntegrityError as error:
            await self._repository.rollback()
            raise UserConflictError from error

        token = self._token_service.create_access_token(user.id)
        return AuthenticationResult(
            access_token=token.value,
            token_type="bearer",
            expires_in=token.expires_in,
            user=to_public_user(user),
        )
