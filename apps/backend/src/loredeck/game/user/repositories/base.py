from dataclasses import dataclass
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


class UserRepository(Protocol):
    async def find_by_username(self, username: str) -> UserModel | None: ...

    async def find_conflicts(self, identifiers: UniqueIdentifiers) -> set[str]: ...

    async def create(self, new_user: NewUser) -> UserModel: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
