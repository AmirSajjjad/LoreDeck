from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from loredeck.game.dependencies import get_draw_reading_use_case
from loredeck.game.exceptions import (
    DeckNotFoundError,
    InactiveDeckError,
    InsufficientActiveCardsError,
)
from loredeck.game.schemas import ReadingCreateRequest, ReadingResponse
from loredeck.game.use_cases import DrawReadingUseCase

router = APIRouter()


@router.post(
    "/readings",
    response_model=ReadingResponse,
    status_code=status.HTTP_200_OK,
)
async def create_reading(
    request: ReadingCreateRequest,
    use_case: Annotated[DrawReadingUseCase, Depends(get_draw_reading_use_case)],
) -> ReadingResponse:
    try:
        result = await use_case.execute(
            deck_id=request.deck_id,
            spread=request.spread,
            question=request.question,
        )
    except (DeckNotFoundError, InactiveDeckError) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found",
        ) from error
    except InsufficientActiveCardsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Deck does not contain enough active cards",
        ) from error

    return ReadingResponse.model_validate(result)
