from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from loredeck.game.user.repositories.base import UNSET, UserProfileUpdate, UserRepository
from loredeck.game.user.repositories.sqlalchemy import SqlAlchemyUserRepository
from loredeck.game.user.schemas.requests import (
    SigninRequest,
    SignupRequest,
    UpdateProfileRequest,
)
from loredeck.game.user.schemas.responses import AuthenticationResponse, PublicUserResponse
from loredeck.game.user.services.password import PasswordService
from loredeck.game.user.services.token import TokenService
from loredeck.game.user.usecases.get_profile import GetProfileUseCase
from loredeck.game.user.usecases.signin import InvalidCredentialsError, SigninUseCase
from loredeck.game.user.usecases.signup import SignupUseCase, UserConflictError
from loredeck.game.user.usecases.update_profile import (
    EmptyProfileUpdateError,
    UpdateProfileUseCase,
)
from loredeck.shared.config import Settings, get_settings
from loredeck.shared.database import get_db_session
from loredeck.shared.models import UserModel

router = APIRouter(prefix="/users", tags=["users"])
bearer_scheme = HTTPBearer(auto_error=False)


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing access token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_password_service() -> PasswordService:
    return PasswordService()


def get_token_service(settings: Annotated[Settings, Depends(get_settings)]) -> TokenService:
    return TokenService(
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
        expire_minutes=settings.jwt_access_token_expire_minutes,
    )


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_signup_use_case(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> SignupUseCase:
    return SignupUseCase(repository, password_service, token_service)


def get_signin_use_case(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> SigninUseCase:
    return SigninUseCase(repository, password_service, token_service)


async def get_optional_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserModel | None:
    if credentials is None:
        return None
    if credentials.scheme.lower() != "bearer":
        raise unauthorized()
    try:
        claims = token_service.decode_access_token(credentials.credentials)
        subject = claims.get("sub")
        if not isinstance(subject, str):
            raise unauthorized()
        user_id = int(subject)
        if user_id <= 0 or str(user_id) != subject:
            raise unauthorized()
    except (jwt.InvalidTokenError, ValueError) as error:
        raise unauthorized() from error

    user = await repository.find_by_id(user_id)
    if user is None:
        raise unauthorized()
    return user


async def get_current_user(
    current_user: Annotated[UserModel | None, Depends(get_optional_current_user)],
) -> UserModel:
    if current_user is None:
        raise unauthorized()
    return current_user


def get_profile_use_case() -> GetProfileUseCase:
    return GetProfileUseCase()


def get_update_profile_use_case(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UpdateProfileUseCase:
    return UpdateProfileUseCase(repository)


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


@router.get("/profile", response_model=PublicUserResponse, status_code=status.HTTP_200_OK)
async def get_profile(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    use_case: Annotated[GetProfileUseCase, Depends(get_profile_use_case)],
) -> PublicUserResponse:
    return PublicUserResponse.model_validate(use_case.execute(current_user))


@router.patch("/profile", response_model=PublicUserResponse, status_code=status.HTTP_200_OK)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    use_case: Annotated[UpdateProfileUseCase, Depends(get_update_profile_use_case)],
) -> PublicUserResponse:
    fields = request.model_fields_set
    update = UserProfileUpdate(
        username=request.username if "username" in fields else UNSET,
        phone_number=request.phone_number if "phone_number" in fields else UNSET,
        profile_pic=request.profile_pic if "profile_pic" in fields else UNSET,
        name=request.name if "name" in fields else UNSET,
        email=str(request.email)
        if request.email is not None
        else (None if "email" in fields else UNSET),
    )
    try:
        result = await use_case.execute(current_user, update)
    except UserConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with one of the supplied identifiers already exists",
        ) from error
    except (EmptyProfileUpdateError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error) or "At least one profile field must be provided",
        ) from error
    return PublicUserResponse.model_validate(result)
