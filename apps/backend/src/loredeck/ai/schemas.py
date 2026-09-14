from pydantic import BaseModel

from loredeck.shared.readings import CardOrientation, ReadingPosition, ReadingSpread


class AICardInput(BaseModel):
    card_id: int
    position: ReadingPosition
    orientation: CardOrientation
    title: str
    description: str
    attributes: dict[str, object]


class GenerateReadingRequest(BaseModel):
    question: str | None
    spread: ReadingSpread
    cards: list[AICardInput]


class GeneratedCardStory(BaseModel):
    card_id: int
    story: str


class GenerateReadingResult(BaseModel):
    cards: list[GeneratedCardStory]
    summary: str
