from enum import StrEnum


class ReadingSpread(StrEnum):
    ONE_CARD = "one_card"
    THREE_CARD = "three_card"


class ReadingPosition(StrEnum):
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


class CardOrientation(StrEnum):
    UPRIGHT = "upright"
    REVERSED = "reversed"
