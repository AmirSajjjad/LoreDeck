from pydantic import BaseModel, ConfigDict, Field

from loredeck.game.use_cases import Orientation, ReadingPosition, Spread


class ReadingCreateRequest(BaseModel):
    question: str | None = None
    deck_id: int = Field(gt=0)
    spread: Spread


class PublicCardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    description: str | None
    number: int | None
    image_path: str | None


class ReadingCardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    position: ReadingPosition
    orientation: Orientation
    card: PublicCardResponse
    story: str


class ReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cards: list[ReadingCardResponse]
    summary: str
