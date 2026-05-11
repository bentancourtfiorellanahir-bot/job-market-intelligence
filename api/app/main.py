from fastapi import FastAPI

from app import models  # noqa: F401
from app.api.routes import router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

app = FastAPI(
    title="Labor Market Intelligence API",
    version="0.1.0",
    description="MVP API for job ingestion, normalization, and retrieval.",
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


app.include_router(router)
