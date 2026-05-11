from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.job import JobPosting
from app.repositories.jobs import JobRepository


class JobService:
    def __init__(self, db: Session) -> None:
        self.repository = JobRepository(db)

    def list_jobs(
        self,
        source: str | None = None,
        q: str | None = None,
        company_name: str | None = None,
        remote_type: str | None = None,
        seniority: str | None = None,
        active_only: bool = True,
        before_last_seen_at: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[JobPosting]:
        return self.repository.list_jobs(
            source=source,
            q=q,
            company_name=company_name,
            remote_type=remote_type,
            seniority=seniority,
            active_only=active_only,
            before_last_seen_at=before_last_seen_at,
            limit=limit,
            offset=offset,
        )

    def get_job_stats(self, source: str | None = None) -> dict[str, Any]:
        return self.repository.get_job_stats(source=source)
