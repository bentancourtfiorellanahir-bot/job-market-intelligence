from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.api.dashboard import render_dashboard_html
from app.db.session import get_db
from app.schemas.job import JobPostingRead, JobStatsRead
from app.services.jobs import JobService

dashboard_router = APIRouter()
router = APIRouter(prefix="/v1")


@dashboard_router.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard", status_code=307)


@dashboard_router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard(
    source: str | None = None,
    q: str | None = Query(default=None, min_length=2),
    remote_type: str | None = None,
    seniority: str | None = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    service = JobService(db)
    jobs = service.list_jobs(
        source=source,
        q=q,
        remote_type=remote_type,
        seniority=seniority,
        active_only=active_only,
        limit=50,
    )
    stats = service.get_job_stats(source=source)
    html = render_dashboard_html(
        stats=stats,
        jobs=jobs,
        filters={
            "source": source,
            "q": q,
            "remote_type": remote_type,
            "seniority": seniority,
            "active_only": active_only,
        },
    )
    return HTMLResponse(content=html)


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
