from prefect import flow, get_run_logger, task

from app import models  # noqa: F401
from app.contracts.jobs import IngestionResult
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.repositories.jobs import JobRepository
from connectors.greenhouse import GreenhouseConnector
from normalizers.jobs import normalize_greenhouse_job
from pydantic_settings import BaseSettings, SettingsConfigDict


class PipelineSettings(BaseSettings):
    greenhouse_board_token: str = "openai"
    greenhouse_timeout_seconds: float = 30.0
    greenhouse_max_attempts: int = 3
    greenhouse_backoff_seconds: float = 1.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = PipelineSettings()


@task
def fetch_jobs() -> list[dict]:
    connector = GreenhouseConnector(
        board_token=settings.greenhouse_board_token,
        timeout_seconds=settings.greenhouse_timeout_seconds,
        max_attempts=settings.greenhouse_max_attempts,
        backoff_seconds=settings.greenhouse_backoff_seconds,
    )
    return connector.fetch_jobs()


@task
def persist_jobs(jobs: list[dict]) -> IngestionResult:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    logger = get_run_logger()
    result: IngestionResult = {
        "seen": len(jobs),
        "inserted": 0,
        "updated": 0,
        "unchanged": 0,
        "snapshots_created": 0,
        "marked_inactive": 0,
        "failed": 0,
    }
    try:
        repository = JobRepository(db)
        active_source_job_ids: set[str] = set()
        for job in jobs:
            try:
                normalized = normalize_greenhouse_job(job, settings.greenhouse_board_token)
                active_source_job_ids.add(normalized["source_job_id"])
                upsert_result = repository.upsert_job(normalized, job)
                result[upsert_result.status] += 1
                if upsert_result.snapshot_created:
                    result["snapshots_created"] += 1
            except (KeyError, TypeError, ValueError) as exc:
                result["failed"] += 1
                logger.warning("Skipping malformed Greenhouse job payload: %s", exc)

        result["marked_inactive"] = repository.mark_missing_jobs_inactive(
            source="greenhouse",
            board_token=settings.greenhouse_board_token,
            active_source_job_ids=active_source_job_ids,
        )
        result["snapshots_created"] += result["marked_inactive"]
        db.commit()
        return result
    finally:
        db.close()


@flow(name="ingest-greenhouse-jobs")
def ingest_greenhouse_jobs() -> IngestionResult:
    logger = get_run_logger()
    jobs = fetch_jobs()
    result = persist_jobs(jobs)
    logger.info(
        (
            "Processed Greenhouse board '%s': seen=%s inserted=%s updated=%s "
            "unchanged=%s snapshots=%s inactive=%s failed=%s"
        ),
        settings.greenhouse_board_token,
        result["seen"],
        result["inserted"],
        result["updated"],
        result["unchanged"],
        result["snapshots_created"],
        result["marked_inactive"],
        result["failed"],
    )
    return result


if __name__ == "__main__":
    ingest_greenhouse_jobs()
