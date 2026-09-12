from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from loredeck.shared.database import Base

if TYPE_CHECKING:
    from loredeck.shared.models.user_card_history import UserCardHistoryModel


class DeckModel(Base):
    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )
    user_card_histories: Mapped[list["UserCardHistoryModel"]] = relationship(
        back_populates="deck",
    )
