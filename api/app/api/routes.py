from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.job import JobPostingRead
from app.services.jobs import JobService

router = APIRouter(prefix="/v1")


@router.get("/jobs", response_model=list[JobPostingRead])
def list_jobs(
    source: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[JobPostingRead]:
    service = JobService(db)
    return service.list_jobs(source=source, limit=limit)

