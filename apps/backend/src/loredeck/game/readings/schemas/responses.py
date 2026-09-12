from pydantic import BaseModel, ConfigDict

from loredeck.game.readings.usecases.create_reading import Orientation, ReadingPosition


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
