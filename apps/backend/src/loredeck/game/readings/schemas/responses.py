from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from loredeck.game.readings.usecases.create_reading import Orientation, ReadingPosition, Spread


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


class HistoryDeckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    title: str


class ReadingHistoryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    created_at: datetime
    question: str | None
    deck: HistoryDeckResponse
    spread: Spread


class ReadingHistoryPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[ReadingHistoryItemResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)


class HistoricalCardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    position: ReadingPosition
    orientation: Orientation
    card: PublicCardResponse
    story: str | None


class ReadingHistoryDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    created_at: datetime
    question: str | None
    deck: HistoryDeckResponse
    spread: Spread
    cards: list[HistoricalCardResponse]
    summary: str | None
