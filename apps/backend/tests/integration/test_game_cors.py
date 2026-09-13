from typing import Protocol, cast

from starlette.testclient import TestClient

from loredeck.game.main import create_app
from loredeck.shared.config import Settings

ALLOWED_ORIGIN = "http://localhost:5173"
DISALLOWED_ORIGIN = "https://example.com"


class HttpResponse(Protocol):
    status_code: int
    headers: dict[str, str]


def build_app() -> TestClient:
    settings = Settings.model_validate(
        {
            "database_host": "localhost",
            "database_port": 5432,
            "database_name": "loredeck",
            "database_user": "loredeck",
            "database_password": "change-me",
            "debug": True,
            "cors_allowed_origins": ALLOWED_ORIGIN,
        }
    )
    return TestClient(create_app(settings))


def test_allowed_origin_receives_cors_response_headers() -> None:
    with build_app() as client:
        response = cast(
            HttpResponse,
            client.get(  # pyright: ignore[reportUnknownMemberType]
                "/openapi.json",
                headers={"Origin": ALLOWED_ORIGIN},
            ),
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"


def test_decks_preflight_request_succeeds_for_allowed_origin() -> None:
    with build_app() as client:
        response = cast(
            HttpResponse,
            client.options(  # pyright: ignore[reportUnknownMemberType]
                "/decks",
                headers={
                    "Origin": ALLOWED_ORIGIN,
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Authorization,Content-Type",
                },
            ),
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"
    assert "GET" in response.headers["access-control-allow-methods"]
    assert "authorization" in response.headers["access-control-allow-headers"].lower()
    assert "content-type" in response.headers["access-control-allow-headers"].lower()


def test_disallowed_origin_is_not_granted_cors_access() -> None:
    with build_app() as client:
        response = cast(
            HttpResponse,
            client.get(  # pyright: ignore[reportUnknownMemberType]
                "/openapi.json",
                headers={"Origin": DISALLOWED_ORIGIN},
            ),
        )

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers
