import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.contracts.jobs import NormalizedJob, UpsertResult
from app.models.job import JobPosting, JobSnapshot


def _stable_hash(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _json_ready(payload: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(payload, default=str))


class JobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

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
        stmt: Select[tuple[JobPosting]] = (
            select(JobPosting).order_by(JobPosting.last_seen_at.desc()).limit(limit)
        )
        if source:
            stmt = stmt.where(JobPosting.source == source)
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    JobPosting.title.ilike(pattern),
                    JobPosting.company_name.ilike(pattern),
                    JobPosting.location_text.ilike(pattern),
                    JobPosting.description_html.ilike(pattern),
                )
            )
        if company_name:
            stmt = stmt.where(JobPosting.company_name.ilike(f"%{company_name}%"))
        if remote_type:
            stmt = stmt.where(JobPosting.remote_type == remote_type)
        if seniority:
            stmt = stmt.where(JobPosting.seniority == seniority)
        if active_only:
            stmt = stmt.where(JobPosting.is_active.is_(True))
        if before_last_seen_at:
            stmt = stmt.where(JobPosting.last_seen_at < before_last_seen_at)
        stmt = stmt.offset(offset)
        return list(self.db.scalars(stmt).all())

    def upsert_job(self, normalized_job: NormalizedJob, raw_job: dict[str, Any]) -> UpsertResult:
        normalized_job = {**normalized_job, "is_active": normalized_job.get("is_active", True)}
        normalized_json = _json_ready(normalized_job)
        raw_json = _json_ready(raw_job)
        normalized_hash = _stable_hash(normalized_json)
        stmt = select(JobPosting).where(
            JobPosting.source == normalized_job["source"],
            JobPosting.source_job_id == normalized_job["source_job_id"],
        )
        record = self.db.scalar(stmt)
        now = datetime.now(timezone.utc)
        status = "unchanged"

        if record is None:
            record = JobPosting(
                **normalized_job,
                raw_json=raw_json,
                first_seen_at=now,
                last_seen_at=now,
            )
            self.db.add(record)
            status = "inserted"
        else:
            for field, value in normalized_job.items():
                setattr(record, field, value)
            record.raw_json = raw_json
            record.last_seen_at = now

        latest_snapshot = self.db.scalar(
            select(JobSnapshot)
            .where(
                JobSnapshot.source == normalized_job["source"],
                JobSnapshot.source_job_id == normalized_job["source_job_id"],
            )
            .order_by(JobSnapshot.observed_at.desc())
            .limit(1)
        )
        latest_hash = _stable_hash(latest_snapshot.normalized_json) if latest_snapshot else None
        snapshot_created = latest_hash != normalized_hash
        if snapshot_created:
            if status == "unchanged":
                status = "updated"
            self.db.add(
                JobSnapshot(
                    source=normalized_job["source"],
                    source_job_id=normalized_job["source_job_id"],
                    normalized_json=normalized_json,
                    raw_json=raw_json,
                    is_active=normalized_job["is_active"],
                )
            )
        self.db.flush()
        return UpsertResult(record=record, status=status, snapshot_created=snapshot_created)

    def mark_missing_jobs_inactive(
        self,
        source: str,
        board_token: str | None,
        active_source_job_ids: set[str],
    ) -> int:
        stmt = select(JobPosting).where(
            JobPosting.source == source,
            JobPosting.is_active.is_(True),
        )
        if board_token:
            stmt = stmt.where(JobPosting.board_token == board_token)

        records = list(self.db.scalars(stmt).all())
        changed = 0
        now = datetime.now(timezone.utc)
        for record in records:
            if record.source_job_id in active_source_job_ids:
                continue

            record.is_active = False
            record.last_seen_at = now
            normalized = self._normalized_payload(record)
            self.db.add(
                JobSnapshot(
                    source=record.source,
                    source_job_id=record.source_job_id,
                    normalized_json=_json_ready(normalized),
                    raw_json=_json_ready(record.raw_json),
                    is_active=False,
                )
            )
            changed += 1

        self.db.flush()
        return changed

    def get_job_stats(self, source: str | None = None) -> dict[str, Any]:
        base = select(JobPosting)
        if source:
            base = base.where(JobPosting.source == source)

        total = self.db.scalar(select(func.count()).select_from(base.subquery())) or 0
        active = (
            self.db.scalar(
                select(func.count()).select_from(
                    base.where(JobPosting.is_active.is_(True)).subquery()
                )
            )
            or 0
        )

        by_remote_type = self._count_by(JobPosting.remote_type, source)
        by_seniority = self._count_by(JobPosting.seniority, source)
        by_source = self._count_by(JobPosting.source, source)

        return {
            "total_jobs": total,
            "active_jobs": active,
            "inactive_jobs": total - active,
            "by_remote_type": by_remote_type,
            "by_seniority": by_seniority,
            "by_source": by_source,
        }

    def _count_by(self, field: ColumnElement, source: str | None) -> dict[str, int]:
        stmt = select(field, func.count()).group_by(field).order_by(func.count().desc())
        if source:
            stmt = stmt.where(JobPosting.source == source)
        return {str(key or "unknown"): count for key, count in self.db.execute(stmt).all()}

    def _normalized_payload(self, record: JobPosting) -> NormalizedJob:
        return {
            "source": record.source,
            "source_job_id": record.source_job_id,
            "board_token": record.board_token,
            "title": record.title,
            "company_name": record.company_name,
            "department": record.department,
            "location_text": record.location_text,
            "employment_type": record.employment_type,
            "remote_type": record.remote_type,
            "seniority": record.seniority,
            "salary_min": record.salary_min,
            "salary_max": record.salary_max,
            "salary_currency": record.salary_currency,
            "skills": record.skills,
            "description_html": record.description_html,
            "apply_url": record.apply_url,
            "posting_url": record.posting_url,
            "published_at": record.published_at,
            "is_active": record.is_active,
        }
