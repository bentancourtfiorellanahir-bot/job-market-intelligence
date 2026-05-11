from prefect import flow, get_run_logger, task

from app import models  # noqa: F401
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.repositories.jobs import JobRepository
from connectors.greenhouse import GreenhouseConnector
from normalizers.jobs import normalize_greenhouse_job
from pydantic_settings import BaseSettings, SettingsConfigDict


class PipelineSettings(BaseSettings):
    greenhouse_board_token: str = "openai"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = PipelineSettings()


@task
def fetch_jobs() -> list[dict]:
    connector = GreenhouseConnector(settings.greenhouse_board_token)
    return connector.fetch_jobs()


@task
def persist_jobs(jobs: list[dict]) -> int:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        repository = JobRepository(db)
        for job in jobs:
            normalized = normalize_greenhouse_job(job, settings.greenhouse_board_token)
            repository.upsert_job(normalized, job)
        db.commit()
        return len(jobs)
    finally:
        db.close()


@flow(name="ingest-greenhouse-jobs")
def ingest_greenhouse_jobs() -> int:
    logger = get_run_logger()
    jobs = fetch_jobs()
    inserted = persist_jobs(jobs)
    logger.info("Ingested %s jobs from Greenhouse board '%s'", inserted, settings.greenhouse_board_token)
    return inserted


if __name__ == "__main__":
    ingest_greenhouse_jobs()
