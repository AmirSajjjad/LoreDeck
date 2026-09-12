from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from loredeck.game.user.repositories.base import (
    NewUser,
    UniqueIdentifiers,
    UnsetType,
    UserProfileUpdate,
)
from loredeck.shared.models import UserModel


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, user_id: int) -> UserModel | None:
        return await self._session.get(UserModel, user_id)

    async def find_by_username(self, username: str) -> UserModel | None:
        return await self._session.scalar(select(UserModel).where(UserModel.username == username))

    async def find_conflicts(
        self,
        identifiers: UniqueIdentifiers,
        *,
        exclude_user_id: int | None = None,
    ) -> set[str]:
        predicates = [UserModel.username == identifiers.username]
        if identifiers.email is not None:
            predicates.append(UserModel.email == identifiers.email)
        if identifiers.phone_number is not None:
            predicates.append(UserModel.phone_number == identifiers.phone_number)
        if identifiers.telegram_id is not None:
            predicates.append(UserModel.telegram_id == identifiers.telegram_id)

        statement = select(UserModel).where(or_(*predicates))
        if exclude_user_id is not None:
            statement = statement.where(UserModel.id != exclude_user_id)
        users = (
            await self._session.scalars(statement.execution_options(populate_existing=True))
        ).all()
        conflicts: set[str] = set()
        for user in users:
            if user.username == identifiers.username:
                conflicts.add("username")
            if identifiers.email is not None and user.email == identifiers.email:
                conflicts.add("email")
            if (
                identifiers.phone_number is not None
                and user.phone_number == identifiers.phone_number
            ):
                conflicts.add("phone_number")
            if identifiers.telegram_id is not None and user.telegram_id == identifiers.telegram_id:
                conflicts.add("telegram_id")
        return conflicts

    async def create(self, new_user: NewUser) -> UserModel:
        user = UserModel(
            username=new_user.username,
            password_hash=new_user.password_hash,
            phone_number=new_user.phone_number,
            profile_pic=new_user.profile_pic,
            name=new_user.name,
            email=new_user.email,
            telegram_id=new_user.telegram_id,
        )
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update_profile(self, user: UserModel, update: UserProfileUpdate) -> UserModel:
        for field_name in ("username", "phone_number", "profile_pic", "name", "email"):
            value = getattr(update, field_name)
            if not isinstance(value, UnsetType):
                setattr(user, field_name, value)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
