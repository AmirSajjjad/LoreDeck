import asyncio
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from loredeck.db.models import CardModel, DeckModel
from loredeck.db.session import get_session_factory


class CardSeedData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    number: int = Field(ge=0)
    image_path: str | None = Field(default=None, max_length=500)
    attributes: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class DeckSeedData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    is_active: bool = True
    cards: list[CardSeedData]


def load_seed_data() -> DeckSeedData:
    data_file = Path(__file__).resolve().with_name("seed_major_arcana.json")

    with data_file.open(encoding="utf-8") as file:
        raw_data = json.load(file)

    return DeckSeedData.model_validate(raw_data)


async def upsert_deck(
    session: AsyncSession,
    seed_data: DeckSeedData,
) -> tuple[DeckModel, bool]:
    result = await session.execute(
        select(DeckModel)
        .where(DeckModel.title == seed_data.title)
        .limit(1)
    )
    deck = result.scalar_one_or_none()

    if deck is None:
        deck = DeckModel(
            title=seed_data.title,
            description=seed_data.description,
            is_active=seed_data.is_active,
        )
        session.add(deck)
        await session.flush()

        return deck, True

    deck.description = seed_data.description
    deck.is_active = seed_data.is_active

    return deck, False


async def upsert_cards(
    session: AsyncSession,
    deck: DeckModel,
    cards: list[CardSeedData],
) -> tuple[int, int]:
    created_count = 0
    updated_count = 0

    for card_data in cards:
        result = await session.execute(
            select(CardModel)
            .where(
                CardModel.deck_id == deck.id,
                CardModel.number == card_data.number,
            )
            .limit(1)
        )
        card = result.scalar_one_or_none()

        if card is None:
            session.add(
                CardModel(
                    deck_id=deck.id,
                    title=card_data.title,
                    description=card_data.description,
                    number=card_data.number,
                    image_path=card_data.image_path,
                    attributes=card_data.attributes,
                    is_active=card_data.is_active,
                )
            )
            created_count += 1
            continue

        card.title = card_data.title
        card.description = card_data.description
        card.number = card_data.number
        card.image_path = card_data.image_path
        card.attributes = card_data.attributes
        card.is_active = card_data.is_active
        updated_count += 1

    return created_count, updated_count


async def seed_major_arcana() -> None:
    seed_data = load_seed_data()
    session_factory = get_session_factory()

    async with session_factory() as session:
        async with session.begin():
            deck, deck_created = await upsert_deck(
                session=session,
                seed_data=seed_data,
            )
            created_count, updated_count = await upsert_cards(
                session=session,
                deck=deck,
                cards=seed_data.cards,
            )

    deck_action = "ایجاد شد" if deck_created else "به‌روزرسانی شد"

    print(f'مجموعه کارت «{seed_data.title}» {deck_action}.')
    print(f"تعداد کارت‌های ایجادشده: {created_count}")
    print(f"تعداد کارت‌های به‌روزرسانی‌شده: {updated_count}")
    print(f"مجموع کارت‌های فایل: {len(seed_data.cards)}")


if __name__ == "__main__":
    asyncio.run(seed_major_arcana())
