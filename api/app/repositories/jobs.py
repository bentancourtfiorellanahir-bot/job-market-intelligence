from datetime import datetime, timezone

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.job import JobPosting, JobSnapshot


class JobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_jobs(self, source: str | None = None, limit: int = 50) -> list[JobPosting]:
        stmt: Select[tuple[JobPosting]] = select(JobPosting).order_by(JobPosting.last_seen_at.desc()).limit(limit)
        if source:
            stmt = stmt.where(JobPosting.source == source)
        return list(self.db.scalars(stmt).all())

    def upsert_job(self, normalized_job: dict, raw_job: dict) -> JobPosting:
        stmt = select(JobPosting).where(
            JobPosting.source == normalized_job["source"],
            JobPosting.source_job_id == normalized_job["source_job_id"],
        )
        record = self.db.scalar(stmt)
        now = datetime.now(timezone.utc)

        if record is None:
            record = JobPosting(
                **normalized_job,
                raw_json=raw_job,
                first_seen_at=now,
                last_seen_at=now,
            )
            self.db.add(record)
        else:
            for field, value in normalized_job.items():
                setattr(record, field, value)
            record.raw_json = raw_job
            record.last_seen_at = now

        snapshot = JobSnapshot(
            source=normalized_job["source"],
            source_job_id=normalized_job["source_job_id"],
            normalized_json=normalized_job,
            raw_json=raw_job,
            is_active=normalized_job.get("is_active", True),
        )
        self.db.add(snapshot)
        self.db.flush()
        return record

