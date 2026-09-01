from loredeck.db.base import Base
from loredeck.db.models import CardModel, DeckModel


def test_deck_model_uses_decks_table() -> None:
    assert DeckModel.__tablename__ == "decks"
    assert "decks" in Base.metadata.tables


def test_card_model_references_deck() -> None:
    card_table = CardModel.__table__

    assert CardModel.__tablename__ == "cards"
    assert "cards" in Base.metadata.tables

    foreign_key = next(iter(card_table.c.deck_id.foreign_keys))

    assert foreign_key.target_fullname == "decks.id"
    assert foreign_key.ondelete == "RESTRICT"
