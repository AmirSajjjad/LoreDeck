from fastapi import FastAPI

from loredeck.game.router import router as readings_router
from loredeck.shared.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    documentation_url = "/docs" if settings.debug else None

    application = FastAPI(
        title="LoreDeck Game API",
        docs_url=documentation_url,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )
    application.include_router(readings_router)
    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("loredeck.game.main:app", host="0.0.0.0", port=8000, reload=True)  # nosec
