from dataclasses import replace

from sqlalchemy.exc import IntegrityError

from loredeck.game.user.repositories.base import (
    UniqueIdentifiers,
    UnsetType,
    UserProfileUpdate,
    UserRepository,
)
from loredeck.game.user.usecases.signup import PublicUser, UserConflictError, to_public_user
from loredeck.shared.models import UserModel


class EmptyProfileUpdateError(ValueError):
    """Raised when a profile update contains no fields."""


class UpdateProfileUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def execute(self, user: UserModel, update: UserProfileUpdate) -> PublicUser:
        if all(
            isinstance(getattr(update, field_name), UnsetType)
            for field_name in ("username", "phone_number", "profile_pic", "name", "email")
        ):
            raise EmptyProfileUpdateError

        normalized = replace(
            update,
            username=(
                update.username.strip() if isinstance(update.username, str) else update.username
            ),
            email=update.email.strip().lower() if isinstance(update.email, str) else update.email,
        )
        if normalized.username is None:
            raise ValueError("username cannot be null")
        if isinstance(normalized.username, str) and not normalized.username:
            raise ValueError("username must not be blank")

        identifiers = UniqueIdentifiers(
            username=(
                normalized.username if isinstance(normalized.username, str) else user.username
            ),
            email=normalized.email if isinstance(normalized.email, str) else None,
            phone_number=(
                normalized.phone_number if isinstance(normalized.phone_number, str) else None
            ),
        )
        if await self._repository.find_conflicts(identifiers, exclude_user_id=user.id):
            raise UserConflictError

        try:
            updated_user = await self._repository.update_profile(user, normalized)
            await self._repository.commit()
        except IntegrityError as error:
            await self._repository.rollback()
            raise UserConflictError from error
        return to_public_user(updated_user)
