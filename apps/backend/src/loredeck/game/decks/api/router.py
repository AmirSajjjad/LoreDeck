from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from loredeck.game.decks.repositories.base import DeckRepository
from loredeck.game.decks.repositories.sqlalchemy import SqlAlchemyDeckRepository
from loredeck.game.decks.schemas.responses import PublicDeckResponse
from loredeck.game.decks.usecases.list_active_decks import ListActiveDecksUseCase
from loredeck.shared.database import get_db_session

router = APIRouter(prefix="/decks", tags=["decks"])


def get_deck_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DeckRepository:
    return SqlAlchemyDeckRepository(session)


def get_list_active_decks_use_case(
    repository: Annotated[DeckRepository, Depends(get_deck_repository)],
) -> ListActiveDecksUseCase:
    return ListActiveDecksUseCase(repository)


@router.get("", response_model=list[PublicDeckResponse], status_code=status.HTTP_200_OK)
async def list_active_decks(
    use_case: Annotated[ListActiveDecksUseCase, Depends(get_list_active_decks_use_case)],
) -> list[PublicDeckResponse]:
    decks = await use_case.execute()
    return [PublicDeckResponse.model_validate(deck) for deck in decks]
