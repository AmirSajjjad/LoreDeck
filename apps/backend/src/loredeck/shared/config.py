from functools import lru_cache

from pydantic import PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LOREDECK_",
        extra="ignore",
    )

    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: SecretStr
    database_driver: str = "postgresql+asyncpg"
    database_echo: bool = False
    debug: bool = False
    cors_allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    jwt_secret: SecretStr = SecretStr("")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: PositiveInt = 30

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername=self.database_driver,
            username=self.database_user,
            password=self.database_password.get_secret_value(),
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]
