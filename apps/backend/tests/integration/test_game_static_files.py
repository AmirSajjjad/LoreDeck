from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, cast

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from loredeck.game.main import create_app
from loredeck.shared.config import Settings

CARD_IMAGE_PATH = "cards/major-arcana/01M22XC8QNG1ZQEFTGJ5D5WJVE.webp"


class HttpResponse(Protocol):
    status_code: int
    headers: dict[str, str]


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


@pytest.fixture(params=[True, False], ids=["debug-enabled", "debug-disabled"])
def client(request: pytest.FixtureRequest) -> Iterator[TestClient]:
    with TestClient(build_app(debug=cast(bool, request.param))) as test_client:
        yield test_client


def test_existing_card_image_is_served(client: TestClient) -> None:
    response = cast(
        HttpResponse,
        client.get(  # pyright: ignore[reportUnknownMemberType]
            f"/static/{CARD_IMAGE_PATH}"
        ),
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/webp"


def test_missing_static_file_returns_not_found(client: TestClient) -> None:
    response = cast(
        HttpResponse,
        client.get(  # pyright: ignore[reportUnknownMemberType]
            "/static/cards/major-arcana/missing.webp"
        ),
    )

    assert response.status_code == 404


def test_file_outside_static_directory_is_not_exposed(client: TestClient) -> None:
    response = cast(
        HttpResponse,
        client.get(  # pyright: ignore[reportUnknownMemberType]
            "/static/%2e%2e/.env.sample"
        ),
    )

    assert response.status_code == 404


def test_static_path_does_not_depend_on_working_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    with TestClient(build_app(debug=False)) as client:
        response = cast(
            HttpResponse,
            client.get(  # pyright: ignore[reportUnknownMemberType]
                f"/static/{CARD_IMAGE_PATH}"
            ),
        )

    assert response.status_code == 200


@pytest.mark.parametrize("debug", [True, False])
def test_readings_route_remains_registered(debug: bool) -> None:
    with TestClient(build_app(debug=debug)) as client:
        response = cast(
            HttpResponse,
            client.post(  # pyright: ignore[reportUnknownMemberType]
                "/readings", json={}
            ),
        )

    assert response.status_code == 422
