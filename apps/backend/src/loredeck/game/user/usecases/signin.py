from loredeck.game.user.repositories.base import UserRepository
from loredeck.game.user.services.password import PasswordService
from loredeck.game.user.services.token import TokenService
from loredeck.game.user.usecases.signup import AuthenticationResult, to_public_user


class InvalidCredentialsError(Exception):
    """Raised for any invalid username/password combination."""


class SigninUseCase:
    def __init__(
        self,
        repository: UserRepository,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:
        self._repository = repository
        self._password_service = password_service
        self._token_service = token_service

    async def execute(self, *, username: str, password: str) -> AuthenticationResult:
        user = await self._repository.find_by_username(username.strip())
        if user is None:
            self._password_service.verify_dummy_password(password)
            raise InvalidCredentialsError
        if not self._password_service.verify_password(password, user.password_hash):
            raise InvalidCredentialsError

        token = self._token_service.create_access_token(user.id)
        return AuthenticationResult(
            access_token=token.value,
            token_type="bearer",
            expires_in=token.expires_in,
            user=to_public_user(user),
        )
