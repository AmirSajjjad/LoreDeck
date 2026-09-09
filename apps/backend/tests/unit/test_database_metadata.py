import re
from pathlib import Path

from loredeck.shared.database import Base
from loredeck.shared.models import CardModel, DeckModel

REVISION_FILENAME = re.compile(r"^\d{3}-\d{8}-[a-z0-9_]+\.py$")


def test_all_models_are_registered() -> None:
    assert set(Base.metadata.tables) == {"cards", "decks"}
    assert CardModel.metadata is Base.metadata
    assert DeckModel.metadata is Base.metadata


def test_revision_filename_convention() -> None:
    versions_dir = Path(__file__).parents[2] / "alembic" / "versions"
    revisions = list(versions_dir.glob("*.py"))

    assert len(revisions) == 1
    assert revisions[0].name.startswith("001-")
    assert REVISION_FILENAME.fullmatch(revisions[0].name)
