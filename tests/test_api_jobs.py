import importlib.util
import sys
import unittest
from pathlib import Path


if importlib.util.find_spec("fastapi") is None or importlib.util.find_spec("sqlalchemy") is None:
    raise unittest.SkipTest("FastAPI or SQLAlchemy is not installed in this runtime")

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"

if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import dashboard_router, router
from app.db.base import Base
from app.db.session import get_db
from app.repositories.jobs import JobRepository


def normalized_job(source_job_id: str, title: str) -> dict:
    return {
        "source": "greenhouse",
        "source_job_id": source_job_id,
        "board_token": "demo",
        "title": title,
        "company_name": "Demo",
        "department": "Engineering",
        "location_text": "Remote",
        "employment_type": "Full-time",
        "remote_type": "remote",
        "seniority": "senior",
        "salary_min": 120000,
        "salary_max": 150000,
        "salary_currency": "USD",
        "skills": ["Python"],
        "description_html": "Python API role",
        "apply_url": "https://example.com/apply",
        "posting_url": "https://example.com/jobs",
        "published_at": None,
        "is_active": True,
    }


class JobsApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            future=True,
        )
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine, future=True)

        session = self.session_factory()
        repository = JobRepository(session)
        repository.upsert_job(normalized_job("job-1", "Senior Backend Engineer"), {"id": "job-1"})
        repository.upsert_job(normalized_job("job-2", "Senior Data Engineer"), {"id": "job-2"})
        session.commit()
        session.close()

        def override_get_db():
            db = self.session_factory()
            try:
                yield db
            finally:
                db.close()

        self.app = FastAPI()
        self.app.include_router(router)
        self.app.include_router(dashboard_router)
        self.app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def test_list_jobs_filters_by_query(self) -> None:
        response = self.client.get("/v1/jobs", params={"q": "backend"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["source_job_id"], "job-1")

    def test_job_stats_endpoint(self) -> None:
        response = self.client.get("/v1/jobs/stats")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_jobs"], 2)
        self.assertEqual(response.json()["active_jobs"], 2)

    def test_dashboard_page_renders(self) -> None:
        response = self.client.get("/dashboard")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Labor Market Intelligence Dashboard", response.text)
        self.assertIn("Senior Backend Engineer", response.text)


if __name__ == "__main__":
    unittest.main()
