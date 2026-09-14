from typing import cast

import pytest
from pydantic import ValidationError

from loredeck.ai.enums import AIProviderName
from loredeck.ai.exceptions import UnsupportedAIProviderError
from loredeck.ai.factory import create_ai_provider
from loredeck.ai.providers.openai import OpenAIProvider
from loredeck.shared.config import Settings


def settings_data() -> dict[str, object]:
    return {
        "database_host": "localhost",
        "database_port": 5432,
        "database_name": "loredeck",
        "database_user": "loredeck",
        "database_password": "test-password",
        "ai_provider": "openai",
        "openai_api_key": "test-key",
        "openai_model": "test-model",
    }


def test_ai_settings_parse_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    environment = {
        "LOREDECK_DATABASE_HOST": "localhost",
        "LOREDECK_DATABASE_PORT": "5432",
        "LOREDECK_DATABASE_NAME": "loredeck",
        "LOREDECK_DATABASE_USER": "loredeck",
        "LOREDECK_DATABASE_PASSWORD": "test-password",
        "LOREDECK_AI_PROVIDER": "openai",
        "LOREDECK_AI_STORY_MAX_CHARACTERS": "351",
        "LOREDECK_AI_SUMMARY_MAX_CHARACTERS": "701",
        "LOREDECK_OPENAI_API_KEY": "test-key",
        "LOREDECK_OPENAI_MODEL": "test-model",
        "LOREDECK_OPENAI_TIMEOUT_SECONDS": "12.5",
        "LOREDECK_OPENAI_MAX_RETRIES": "4",
    }
    for name, value in environment.items():
        monkeypatch.setenv(name, value)

    settings = Settings(_env_file=None)  # pyright: ignore[reportCallIssue]

    assert settings.ai_provider == AIProviderName.OPENAI
    assert settings.ai_story_max_characters == 351
    assert settings.ai_summary_max_characters == 701
    assert settings.openai_api_key is not None
    assert settings.openai_api_key.get_secret_value() == "test-key"
    assert settings.openai_model == "test-model"
    assert settings.openai_timeout_seconds == 12.5
    assert settings.openai_max_retries == 4


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("ai_story_max_characters", 0),
        ("ai_summary_max_characters", -1),
        ("openai_timeout_seconds", 0),
        ("openai_max_retries", -1),
    ],
)
def test_ai_numeric_configuration_rejects_invalid_values(field: str, value: int) -> None:
    data = settings_data()
    data[field] = value
    with pytest.raises(ValidationError):
        Settings.model_validate(data)


@pytest.mark.parametrize(("field", "value"), [("openai_api_key", ""), ("openai_model", " ")])
def test_openai_configuration_is_required_when_selected(field: str, value: str) -> None:
    data = settings_data()
    data[field] = value
    with pytest.raises(ValidationError):
        Settings.model_validate(data)


def test_factory_selects_openai_provider() -> None:
    provider = create_ai_provider(Settings.model_validate(settings_data()))

    assert isinstance(provider, OpenAIProvider)
    assert provider.model == "test-model"


def test_factory_rejects_unsupported_provider() -> None:
    settings = Settings.model_validate(settings_data())
    object.__setattr__(settings, "ai_provider", cast(AIProviderName, "unsupported"))

    with pytest.raises(UnsupportedAIProviderError):
        create_ai_provider(settings)
