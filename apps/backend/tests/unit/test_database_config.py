from sqlalchemy import make_url

from loredeck.shared.config import Settings


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
