from functools import lru_cache
from pathlib import Path

from pydantic import NonNegativeInt, PositiveFloat, PositiveInt, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from loredeck.ai.enums import AIProviderName

BACKEND_DIRECTORY = Path(__file__).resolve().parents[3]
ENV_FILE = BACKEND_DIRECTORY / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
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
    cors_allowed_methods: str = "*"
    cors_allowed_headers: str = "*"
    jwt_secret: SecretStr = SecretStr("")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: PositiveInt = 30
    ai_provider: AIProviderName
    ai_story_max_characters: PositiveInt = 350
    ai_summary_max_characters: PositiveInt = 700
    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: SecretStr | None = None
    openai_model: str | None = None
    openai_timeout_seconds: PositiveFloat = 30
    openai_max_retries: NonNegativeInt = 2

    @model_validator(mode="after")
    def validate_ai_provider_configuration(self) -> "Settings":
        if self.ai_provider == AIProviderName.OPENAI:
            if self.openai_api_key is None or not self.openai_api_key.get_secret_value().strip():
                raise ValueError("OpenAI API key is required when the OpenAI provider is selected")
            if self.openai_model is None or not self.openai_model.strip():
                raise ValueError("OpenAI model is required when the OpenAI provider is selected")
        return self

    @property
    def allowed_origins(self) -> list[str]:
        return self._split_csv(self.cors_allowed_origins)

    @property
    def allowed_methods(self) -> list[str]:
        return self._split_csv(self.cors_allowed_methods)

    @property
    def allowed_headers(self) -> list[str]:
        return self._split_csv(self.cors_allowed_headers)

    @staticmethod
    def _split_csv(value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

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
