from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from loredeck.game.readings.repositories.history import (
    ReadingHistoryRepository,
    SqlAlchemyReadingHistoryRepository,
)
from loredeck.game.readings.repositories.sqlalchemy import SqlAlchemyReadingRepository
from loredeck.game.readings.schemas.requests import ReadingCreateRequest
from loredeck.game.readings.schemas.responses import (
    ReadingHistoryDetailResponse,
    ReadingHistoryPageResponse,
    ReadingResponse,
)
from loredeck.game.readings.usecases.create_reading import (
    DeckNotFoundError,
    DrawReadingUseCase,
    InactiveDeckError,
    InsufficientActiveCardsError,
    ReadingPersistenceError,
)
from loredeck.game.readings.usecases.history import (
    GetReadingHistoryUseCase,
    HistoryNotFoundError,
    ListReadingHistoryUseCase,
)
from loredeck.game.user.api.router import get_current_user, get_optional_current_user
from loredeck.shared.database import get_db_session
from loredeck.shared.models import UserModel

router = APIRouter(prefix="/readings", tags=["readings"])


def get_draw_reading_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DrawReadingUseCase:
    return DrawReadingUseCase(SqlAlchemyReadingRepository(session))


def get_reading_history_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ReadingHistoryRepository:
    return SqlAlchemyReadingHistoryRepository(session)


def get_list_reading_history_use_case(
    repository: Annotated[ReadingHistoryRepository, Depends(get_reading_history_repository)],
) -> ListReadingHistoryUseCase:
    return ListReadingHistoryUseCase(repository)


def get_reading_history_use_case(
    repository: Annotated[ReadingHistoryRepository, Depends(get_reading_history_repository)],
) -> GetReadingHistoryUseCase:
    return GetReadingHistoryUseCase(repository)


@router.get("/history", response_model=ReadingHistoryPageResponse)
async def list_reading_history(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    use_case: Annotated[ListReadingHistoryUseCase, Depends(get_list_reading_history_use_case)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ReadingHistoryPageResponse:
    result = await use_case.execute(current_user.id, limit=limit, offset=offset)
    return ReadingHistoryPageResponse.model_validate(result)


@router.get("/history/{history_id}", response_model=ReadingHistoryDetailResponse)
async def get_reading_history(
    history_id: int,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    use_case: Annotated[GetReadingHistoryUseCase, Depends(get_reading_history_use_case)],
) -> ReadingHistoryDetailResponse:
    try:
        result = await use_case.execute(current_user.id, history_id)
    except HistoryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reading not found"
        ) from error
    return ReadingHistoryDetailResponse.model_validate(result)


@router.post(
    "",
    response_model=ReadingResponse,
    status_code=status.HTTP_200_OK,
    openapi_extra={"security": [{}]},
)
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
