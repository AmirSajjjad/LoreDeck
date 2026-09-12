from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from loredeck.shared.database import Base

if TYPE_CHECKING:
    from loredeck.shared.models.user_card_history import UserCardHistoryModel


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        UniqueConstraint("phone_number", name="uq_users_phone_number"),
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("telegram_id", name="uq_users_telegram_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    phone_number: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    profile_pic: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    card_histories: Mapped[list["UserCardHistoryModel"]] = relationship(
        back_populates="user",
    )
