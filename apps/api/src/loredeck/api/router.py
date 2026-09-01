from typing import Literal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from loredeck.api.dependencies import DatabaseSession


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class ReadinessResponse(BaseModel):
    status: Literal["ready"]
    database: Literal["available"]


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API health",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="loredeck-api",
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Check API dependencies",
)
async def readiness_check(session: DatabaseSession) -> ReadinessResponse:
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from error

    return ReadinessResponse(
        status="ready",
        database="available",
    )
