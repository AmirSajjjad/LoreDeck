import pytest
from pydantic import ValidationError
from sqlalchemy import make_url

from loredeck.shared.config import Settings

DATABASE_ENVIRONMENT = {
    "LOREDECK_DATABASE_HOST": "localhost",
    "LOREDECK_DATABASE_PORT": "5432",
    "LOREDECK_DATABASE_NAME": "loredeck",
    "LOREDECK_DATABASE_USER": "loredeck",
    "LOREDECK_DATABASE_PASSWORD": "change-me",
}


def build_settings_from_environment(
    monkeypatch: pytest.MonkeyPatch,
    *,
    debug: str | None,
) -> Settings:
    for name, value in DATABASE_ENVIRONMENT.items():
        monkeypatch.setenv(name, value)

    if debug is None:
        monkeypatch.delenv("LOREDECK_DEBUG", raising=False)
    else:
        monkeypatch.setenv("LOREDECK_DEBUG", debug)

    return Settings(_env_file=None)  # pyright: ignore[reportCallIssue]


def test_database_url_uses_typed_components() -> None:
    settings = Settings.model_validate(
        {
            "database_host": "localhost",
            "database_port": 5432,
            "database_name": "loredeck",
            "database_user": "reader@example.com",
            "database_password": "p@ss:/?#[]",
        }
    )

    rendered_url = settings.database_url.render_as_string(hide_password=False)
    parsed_url = make_url(rendered_url)

    assert parsed_url.drivername == "postgresql+asyncpg"
    assert parsed_url.username == "reader@example.com"
    assert parsed_url.password == "p@ss:/?#[]"
    assert parsed_url.port == 5432
    assert parsed_url.database == "loredeck"
    assert "reader%40example.com" in rendered_url
    assert "p%40ss%3A%2F%3F%23%5B%5D" in rendered_url


@pytest.mark.parametrize(("environment_value", "expected"), [("true", True), ("false", False)])
def test_debug_uses_pydantic_boolean_parsing(
    monkeypatch: pytest.MonkeyPatch,
    environment_value: str,
    expected: bool,
) -> None:
    settings = build_settings_from_environment(monkeypatch, debug=environment_value)

    assert settings.debug is expected


def test_debug_defaults_to_false(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = build_settings_from_environment(monkeypatch, debug=None)

    assert settings.debug is False


def test_cors_allowed_origins_parses_comma_separated_environment_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name, value in DATABASE_ENVIRONMENT.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setenv(
        "LOREDECK_CORS_ALLOWED_ORIGINS",
        " http://localhost:5173, http://127.0.0.1:5173, ",
    )

    settings = Settings(_env_file=None)  # pyright: ignore[reportCallIssue]

    assert settings.allowed_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def test_jwt_configuration_defaults_and_parsing() -> None:
    settings = Settings.model_validate(
        {
            "database_host": "localhost",
            "database_port": 5432,
            "database_name": "loredeck",
            "database_user": "loredeck",
            "database_password": "change-me",
            "jwt_secret": "test-secret",
            "jwt_access_token_expire_minutes": 15,
        }
    )
    assert settings.jwt_secret.get_secret_value() == "test-secret"
    assert settings.jwt_algorithm == "HS256"
    assert settings.jwt_access_token_expire_minutes == 15


def test_jwt_expiration_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate(
            {
                "database_host": "localhost",
                "database_port": 5432,
                "database_name": "loredeck",
                "database_user": "loredeck",
                "database_password": "change-me",
                "jwt_access_token_expire_minutes": 0,
            }
        )
