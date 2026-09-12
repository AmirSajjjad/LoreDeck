from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from loredeck.game.user.repositories.sqlalchemy import SqlAlchemyUserRepository
from loredeck.game.user.schemas.requests import SigninRequest, SignupRequest
from loredeck.game.user.schemas.responses import AuthenticationResponse
from loredeck.game.user.services.password import PasswordService
from loredeck.game.user.services.token import TokenService
from loredeck.game.user.usecases.signin import InvalidCredentialsError, SigninUseCase
from loredeck.game.user.usecases.signup import SignupUseCase, UserConflictError
from loredeck.shared.config import Settings, get_settings
from loredeck.shared.database import get_db_session

router = APIRouter(prefix="/users", tags=["users"])


def get_password_service() -> PasswordService:
    return PasswordService()


def get_token_service(settings: Annotated[Settings, Depends(get_settings)]) -> TokenService:
    return TokenService(
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
        expire_minutes=settings.jwt_access_token_expire_minutes,
    )


def get_signup_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> SignupUseCase:
    return SignupUseCase(SqlAlchemyUserRepository(session), password_service, token_service)


def get_signin_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> SigninUseCase:
    return SigninUseCase(SqlAlchemyUserRepository(session), password_service, token_service)


@router.post("/signup", response_model=AuthenticationResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    use_case: Annotated[SignupUseCase, Depends(get_signup_use_case)],
) -> AuthenticationResponse:
    try:
        result = await use_case.execute(**request.model_dump(mode="python"))
    except UserConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with one of the supplied identifiers already exists",
        ) from error
    return AuthenticationResponse.model_validate(result)


@router.post("/signin", response_model=AuthenticationResponse, status_code=status.HTTP_200_OK)
async def signin(
    request: SigninRequest,
    use_case: Annotated[SigninUseCase, Depends(get_signin_use_case)],
) -> AuthenticationResponse:
    try:
        result = await use_case.execute(username=request.username, password=request.password)
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    return AuthenticationResponse.model_validate(result)
