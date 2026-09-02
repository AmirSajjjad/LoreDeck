from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from loredeck.api.router import router as api_router
from loredeck.core.config import get_settings

STATIC_DIRECTORY = Path(__file__).resolve().parents[2] / "static"


def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
    )

    application.mount(
        "/media",
        StaticFiles(directory=str(STATIC_DIRECTORY)),
        name="media",
    )

    application.include_router(
        api_router,
        prefix=settings.api_v1_prefix,
    )

    return application


app = create_app()
