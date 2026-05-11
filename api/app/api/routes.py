from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.job import JobPostingRead, JobStatsRead
from app.services.jobs import JobService

router = APIRouter(prefix="/v1")


@router.get("/jobs", response_model=list[JobPostingRead])
def list_jobs(
    source: str | None = None,
    q: str | None = Query(default=None, min_length=2),
    company_name: str | None = None,
    remote_type: str | None = None,
    seniority: str | None = None,
    active_only: bool = True,
    before_last_seen_at: datetime | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[JobPostingRead]:
    service = JobService(db)
    return service.list_jobs(
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


@router.get("/jobs/stats", response_model=JobStatsRead)
def get_job_stats(
    source: str | None = None,
    db: Session = Depends(get_db),
) -> JobStatsRead:
    service = JobService(db)
    return JobStatsRead(**service.get_job_stats(source=source))
