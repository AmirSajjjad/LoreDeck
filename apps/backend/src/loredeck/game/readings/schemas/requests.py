from pydantic import BaseModel, Field

from loredeck.game.readings.usecases.create_reading import Spread


class ReadingCreateRequest(BaseModel):
    question: str | None = None
    deck_id: int = Field(gt=0)
    spread: Spread
