import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobPostingRead(BaseModel):
    id: uuid.UUID
    source: str
    source_job_id: str
    board_token: str | None
    title: str
    company_name: str | None
    department: str | None
    location_text: str | None
    employment_type: str | None
    remote_type: str | None
    seniority: str | None
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    skills: list[str]
    apply_url: str | None
    posting_url: str | None
    published_at: datetime | None
    first_seen_at: datetime
    last_seen_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class JobStatsRead(BaseModel):
    total_jobs: int
    active_jobs: int
    inactive_jobs: int
    by_remote_type: dict[str, int]
    by_seniority: dict[str, int]
    by_source: dict[str, int]
