from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from loredeck.game.readings.repositories.sqlalchemy import SqlAlchemyReadingRepository
from loredeck.game.readings.schemas.requests import ReadingCreateRequest
from loredeck.game.readings.schemas.responses import ReadingResponse
from loredeck.game.readings.usecases.create_reading import (
    DeckNotFoundError,
    DrawReadingUseCase,
    InactiveDeckError,
    InsufficientActiveCardsError,
    ReadingPersistenceError,
)
from loredeck.game.user.api.router import get_optional_current_user
from loredeck.shared.database import get_db_session
from loredeck.shared.models import UserModel

router = APIRouter(prefix="/readings", tags=["readings"])


def get_draw_reading_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DrawReadingUseCase:
    return DrawReadingUseCase(SqlAlchemyReadingRepository(session))


@router.post("", response_model=ReadingResponse, status_code=status.HTTP_200_OK)
async def create_reading(
    request: ReadingCreateRequest,
    use_case: Annotated[DrawReadingUseCase, Depends(get_draw_reading_use_case)],
    current_user: Annotated[UserModel | None, Depends(get_optional_current_user)],
) -> ReadingResponse:
    try:
        result = await use_case.execute(
            deck_id=request.deck_id,
            spread=request.spread,
            question=request.question,
            user_id=current_user.id if current_user is not None else None,
        )
    except (DeckNotFoundError, InactiveDeckError) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found"
        ) from error
    except InsufficientActiveCardsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Deck does not contain enough active cards",
        ) from error
    except ReadingPersistenceError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reading could not be saved",
        ) from error

    return ReadingResponse.model_validate(result)
