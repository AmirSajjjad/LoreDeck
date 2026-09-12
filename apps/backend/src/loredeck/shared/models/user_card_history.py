from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from loredeck.shared.database import Base
from loredeck.shared.models.card import CardModel
from loredeck.shared.models.deck import DeckModel
from loredeck.shared.models.user import UserModel


class UserCardHistoryModel(Base):
    __tablename__ = "user_card_histories"
    __table_args__ = (
        CheckConstraint(
            "second_card_id IS NOT NULL OR third_card_id IS NULL",
            name="card_sequence",
        ),
        CheckConstraint(
            "first_card_id <> second_card_id",
            name="first_second_cards_differ",
        ),
        CheckConstraint(
            "first_card_id <> third_card_id",
            name="first_third_cards_differ",
        ),
        CheckConstraint(
            "second_card_id <> third_card_id",
            name="second_third_cards_differ",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    question: Mapped[str | None] = mapped_column(Text, nullable=True)
    deck_id: Mapped[int] = mapped_column(
        ForeignKey("decks.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    first_card_id: Mapped[int] = mapped_column(
        ForeignKey("cards.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    first_story: Mapped[str | None] = mapped_column(Text, nullable=True)
    second_card_id: Mapped[int | None] = mapped_column(
        ForeignKey("cards.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    second_story: Mapped[str | None] = mapped_column(Text, nullable=True)
    third_card_id: Mapped[int | None] = mapped_column(
        ForeignKey("cards.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    third_story: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[UserModel] = relationship(back_populates="card_histories")
    deck: Mapped[DeckModel] = relationship(back_populates="user_card_histories")
    first_card: Mapped[CardModel] = relationship(
        back_populates="first_position_histories",
        foreign_keys=[first_card_id],
    )
    second_card: Mapped[CardModel | None] = relationship(
        back_populates="second_position_histories",
        foreign_keys=[second_card_id],
    )
    third_card: Mapped[CardModel | None] = relationship(
        back_populates="third_position_histories",
        foreign_keys=[third_card_id],
    )
