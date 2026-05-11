from dataclasses import dataclass
from datetime import datetime
from typing import Literal, TypedDict

from app.models.job import JobPosting


class NormalizedJob(TypedDict):
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
    description_html: str | None
    apply_url: str | None
    posting_url: str | None
    published_at: datetime | None
    is_active: bool


class IngestionResult(TypedDict):
    seen: int
    inserted: int
    updated: int
    unchanged: int
    snapshots_created: int
    marked_inactive: int
    failed: int


UpsertStatus = Literal["inserted", "updated", "unchanged"]


@dataclass(frozen=True)
class UpsertResult:
    record: JobPosting
    status: UpsertStatus
    snapshot_created: bool
