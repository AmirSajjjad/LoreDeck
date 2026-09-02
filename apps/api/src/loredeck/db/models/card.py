from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, true
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from loredeck.db.base import Base


class CardModel(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    deck_id: Mapped[int] = mapped_column(
        ForeignKey(
            "decks.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    number: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )
    image_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    attributes: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )
