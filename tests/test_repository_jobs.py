import importlib.util
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


if importlib.util.find_spec("sqlalchemy") is None:
    raise unittest.SkipTest("SQLAlchemy is not installed in this runtime")

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"

if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.job import JobPosting, JobSnapshot
from app.repositories.jobs import JobRepository


def normalized_job(source_job_id: str = "job-1", title: str = "Data Engineer") -> dict:
    return {
        "source": "greenhouse",
        "source_job_id": source_job_id,
        "board_token": "demo",
        "title": title,
        "company_name": "Demo",
        "department": "Data",
        "location_text": "Remote",
        "employment_type": "Full-time",
        "remote_type": "remote",
        "seniority": "mid",
        "salary_min": None,
        "salary_max": None,
        "salary_currency": None,
        "skills": ["Python", "SQL"],
        "description_html": "Build data products with Python and SQL.",
        "apply_url": "https://example.com/apply",
        "posting_url": "https://example.com/jobs/job-1",
        "published_at": None,
        "is_active": True,
    }


class JobRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
        Base.metadata.create_all(engine)
        self.session = sessionmaker(bind=engine, future=True)()
        self.repository = JobRepository(self.session)

    def tearDown(self) -> None:
        self.session.close()

    def test_upsert_deduplicates_unchanged_snapshots(self) -> None:
        first = self.repository.upsert_job(normalized_job(), {"id": "job-1"})
        second = self.repository.upsert_job(normalized_job(), {"id": "job-1"})

        snapshots = self.session.scalars(select(JobSnapshot)).all()

        self.assertEqual(first.status, "inserted")
        self.assertEqual(second.status, "unchanged")
        self.assertTrue(first.snapshot_created)
        self.assertFalse(second.snapshot_created)
        self.assertEqual(len(snapshots), 1)

    def test_upsert_creates_snapshot_when_normalized_payload_changes(self) -> None:
        self.repository.upsert_job(normalized_job(), {"id": "job-1"})
        changed = self.repository.upsert_job(
            normalized_job(title="Senior Data Engineer"),
            {"id": "job-1"},
        )

        snapshots = self.session.scalars(select(JobSnapshot)).all()

        self.assertEqual(changed.status, "updated")
        self.assertTrue(changed.snapshot_created)
        self.assertEqual(len(snapshots), 2)

    def test_mark_missing_jobs_inactive(self) -> None:
        self.repository.upsert_job(normalized_job("job-1"), {"id": "job-1"})
        self.repository.upsert_job(normalized_job("job-2"), {"id": "job-2"})

        changed = self.repository.mark_missing_jobs_inactive(
            source="greenhouse",
            board_token="demo",
            active_source_job_ids={"job-1"},
        )

        inactive = self.session.scalar(
            select(JobPosting).where(JobPosting.source_job_id == "job-2")
        )

        self.assertEqual(changed, 1)
        self.assertFalse(inactive.is_active)

    def test_list_jobs_filters_and_searches(self) -> None:
        self.repository.upsert_job(normalized_job("job-1", "Data Engineer"), {"id": "job-1"})
        self.repository.upsert_job(normalized_job("job-2", "Frontend Engineer"), {"id": "job-2"})

        results = self.repository.list_jobs(q="data", remote_type="remote")

        self.assertEqual([job.source_job_id for job in results], ["job-1"])

    def test_get_job_stats(self) -> None:
        self.repository.upsert_job(normalized_job("job-1"), {"id": "job-1"})
        self.repository.upsert_job(normalized_job("job-2"), {"id": "job-2"})
        self.repository.mark_missing_jobs_inactive("greenhouse", "demo", {"job-1"})

        stats = self.repository.get_job_stats()

        self.assertEqual(stats["total_jobs"], 2)
        self.assertEqual(stats["active_jobs"], 1)
        self.assertEqual(stats["inactive_jobs"], 1)
        self.assertEqual(stats["by_remote_type"]["remote"], 2)

    def test_upsert_serializes_datetimes_for_json_columns(self) -> None:
        job = normalized_job("job-3")
        job["published_at"] = datetime(2026, 5, 11, tzinfo=timezone.utc)

        result = self.repository.upsert_job(job, {"id": "job-3", "updated_at": job["published_at"]})
        snapshot = self.session.scalars(select(JobSnapshot)).all()[0]

        self.assertEqual(result.status, "inserted")
        self.assertEqual(snapshot.normalized_json["published_at"], "2026-05-11 00:00:00+00:00")
        self.assertEqual(snapshot.raw_json["updated_at"], "2026-05-11 00:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
