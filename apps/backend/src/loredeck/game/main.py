from fastapi import FastAPI

from loredeck.game.router import router as readings_router

app = FastAPI(title="LoreDeck Game API")
app.include_router(readings_router)
