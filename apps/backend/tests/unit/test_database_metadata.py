import re
from pathlib import Path

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import RelationshipProperty

from loredeck.shared.database import Base
from loredeck.shared.models import (
    CardModel,
    DeckModel,
    UserCardHistoryModel,
    UserModel,
)

REVISION_FILENAME = re.compile(r"^\d{3}-\d{8}-[a-z0-9_]+\.py$")


def test_all_models_are_registered() -> None:
    assert set(Base.metadata.tables) == {
        "cards",
        "decks",
        "user_card_histories",
        "users",
    }
    assert CardModel.metadata is Base.metadata
    assert DeckModel.metadata is Base.metadata
    assert UserModel.metadata is Base.metadata
    assert UserCardHistoryModel.metadata is Base.metadata


def test_user_identity_columns_are_unique_and_indexed() -> None:
    user_table = Base.metadata.tables["users"]
    unique_columns = {
        next(iter(constraint.columns)).name
        for constraint in user_table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    indexed_columns = {
        next(iter(index.columns)).name for index in user_table.indexes if len(index.columns) == 1
    }

    assert unique_columns == {"email", "phone_number", "telegram_id", "username"}
    assert indexed_columns == unique_columns
    assert "password" not in user_table.columns
    assert user_table.c.password_hash.nullable is False


def test_history_card_columns_and_constraints() -> None:
    history_table = Base.metadata.tables["user_card_histories"]
    check_names = {
        constraint.name
        for constraint in history_table.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert history_table.c.user_id.nullable is False
    assert history_table.c.deck_id.nullable is False
    assert history_table.c.first_card_id.nullable is False
    assert history_table.c.second_card_id.nullable is True
    assert history_table.c.third_card_id.nullable is True
    assert check_names == {
        "ck_user_card_histories_card_sequence",
        "ck_user_card_histories_first_second_cards_differ",
        "ck_user_card_histories_first_third_cards_differ",
        "ck_user_card_histories_second_third_cards_differ",
    }


def test_history_relationships_use_unambiguous_foreign_keys() -> None:
    mapper = UserCardHistoryModel.__mapper__
    card_relationships = CardModel.__mapper__.relationships

    assert mapper.relationships.user.back_populates == "card_histories"
    assert mapper.relationships.deck.back_populates == "user_card_histories"
    assert _foreign_key_names(mapper.relationships.first_card) == {"first_card_id"}
    assert _foreign_key_names(mapper.relationships.second_card) == {"second_card_id"}
    assert _foreign_key_names(mapper.relationships.third_card) == {"third_card_id"}
    assert card_relationships.first_position_histories.back_populates == "first_card"
    assert card_relationships.second_position_histories.back_populates == "second_card"
    assert card_relationships.third_position_histories.back_populates == "third_card"


def _foreign_key_names(relationship: RelationshipProperty[object]) -> set[str]:
    return {column.name for column in relationship.local_columns}


def test_revision_filename_convention() -> None:
    versions_dir = Path(__file__).parents[2] / "alembic" / "versions"
    revisions = list(versions_dir.glob("*.py"))

    assert len(revisions) == 2
    assert {revision.name[:3] for revision in revisions} == {"001", "002"}
    assert all(REVISION_FILENAME.fullmatch(revision.name) for revision in revisions)
