from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from loredeck.game.repositories import SqlAlchemyReadingRepository
from loredeck.game.use_cases import DrawReadingUseCase
from loredeck.shared.database import get_db_session


def get_draw_reading_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DrawReadingUseCase:
    return DrawReadingUseCase(SqlAlchemyReadingRepository(session))
