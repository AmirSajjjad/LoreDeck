from typing import Protocol, cast

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from loredeck.game.main import create_app
from loredeck.shared.config import Settings


class HttpResponse(Protocol):
    status_code: int

    def json(self) -> object: ...


def build_app(*, debug: bool) -> FastAPI:
    settings = Settings.model_validate(
        {
            "database_host": "localhost",
            "database_port": 5432,
            "database_name": "loredeck",
            "database_user": "loredeck",
            "database_password": "change-me",
            "debug": debug,
        }
    )
    return create_app(settings)


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_documentation_is_available_when_debug_enabled(path: str) -> None:
    with TestClient(build_app(debug=True)) as client:
        response = cast(
            HttpResponse,
            client.get(path),  # pyright: ignore[reportUnknownMemberType]
        )

    assert response.status_code == 200
    if path == "/openapi.json":
        schema = cast(dict[str, object], response.json())
        assert schema["openapi"]


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_documentation_is_unavailable_when_debug_disabled(path: str) -> None:
    with TestClient(build_app(debug=False)) as client:
        response = cast(
            HttpResponse,
            client.get(path),  # pyright: ignore[reportUnknownMemberType]
        )

    assert response.status_code == 404


@pytest.mark.parametrize("debug", [True, False])
def test_readings_route_is_registered_regardless_of_debug(debug: bool) -> None:
    with TestClient(build_app(debug=debug)) as client:
        response = cast(
            HttpResponse,
            client.post(  # pyright: ignore[reportUnknownMemberType]
                "/readings", json={}
            ),
        )

    assert response.status_code == 422


def test_openapi_registers_user_and_reading_routes() -> None:
    with TestClient(build_app(debug=True)) as client:
        response = cast(
            HttpResponse,
            client.get("/openapi.json"),  # pyright: ignore[reportUnknownMemberType]
        )

    schema = cast(dict[str, object], response.json())
    paths = cast(dict[str, object], schema["paths"])
    assert {"/users/signup", "/users/signin", "/readings"} <= paths.keys()
