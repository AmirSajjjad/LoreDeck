from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from loredeck.game.decks.api.router import router as decks_router
from loredeck.game.readings.api.router import router as readings_router
from loredeck.game.user.api.router import router as users_router
from loredeck.shared.config import Settings, get_settings

STATIC_DIRECTORY = Path(__file__).resolve().parents[3] / "static"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    documentation_url = "/docs" if settings.debug else None

    application = FastAPI(
        title="LoreDeck Game API",
        docs_url=documentation_url,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(decks_router)
    application.include_router(readings_router)
    application.include_router(users_router)
    application.mount(
        "/static",
        StaticFiles(directory=STATIC_DIRECTORY),
        name="static",
    )
    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("loredeck.game.main:app", host="0.0.0.0", port=8000, reload=True)  # nosec
