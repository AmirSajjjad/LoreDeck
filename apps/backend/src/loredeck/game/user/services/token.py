from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pydantic import SecretStr


class InvalidTokenConfigurationError(ValueError):
    """Raised when access-token configuration is unusable."""


@dataclass(frozen=True)
class AccessToken:
    value: str
    expires_in: int


class TokenService:
    def __init__(self, *, secret: SecretStr, algorithm: str, expire_minutes: int) -> None:
        secret_value = secret.get_secret_value().strip()
        if not secret_value:
            raise InvalidTokenConfigurationError("LOREDECK_JWT_SECRET must be configured")
        if not algorithm.strip():
            raise InvalidTokenConfigurationError("LOREDECK_JWT_ALGORITHM must be configured")
        if expire_minutes <= 0:
            raise InvalidTokenConfigurationError(
                "LOREDECK_JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be positive"
            )
        self._secret = secret_value
        self._algorithm = algorithm
        self._expires_in = expire_minutes * 60

    def create_access_token(self, user_id: int) -> AccessToken:
        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(seconds=self._expires_in)
        encoded = jwt.encode(  # pyright: ignore[reportUnknownMemberType]
            {"sub": str(user_id), "iat": issued_at, "exp": expires_at},
            self._secret,
            algorithm=self._algorithm,
        )
        return AccessToken(value=encoded, expires_in=self._expires_in)

    def decode_access_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(  # pyright: ignore[reportUnknownMemberType]
            token, self._secret, algorithms=[self._algorithm]
        )
