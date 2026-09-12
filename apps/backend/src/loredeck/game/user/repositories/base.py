from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from loredeck.shared.models import UserModel


@dataclass(frozen=True)
class NewUser:
    username: str
    password_hash: str
    phone_number: str | None
    profile_pic: str | None
    name: str | None
    email: str | None
    telegram_id: int | None


@dataclass(frozen=True)
class UniqueIdentifiers:
    username: str
    email: str | None = None
    phone_number: str | None = None
    telegram_id: int | None = None


class UnsetType(Enum):
    VALUE = "unset"


UNSET = UnsetType.VALUE


@dataclass(frozen=True)
class UserProfileUpdate:
    username: str | UnsetType | None = UNSET
    phone_number: str | UnsetType | None = UNSET
    profile_pic: str | UnsetType | None = UNSET
    name: str | UnsetType | None = UNSET
    email: str | UnsetType | None = UNSET


class UserRepository(Protocol):
    async def find_by_id(self, user_id: int) -> UserModel | None: ...

    async def find_by_username(self, username: str) -> UserModel | None: ...

    async def find_conflicts(
        self,
        identifiers: UniqueIdentifiers,
        *,
        exclude_user_id: int | None = None,
    ) -> set[str]: ...

    async def create(self, new_user: NewUser) -> UserModel: ...

    async def update_profile(self, user: UserModel, update: UserProfileUpdate) -> UserModel: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
