import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINES_DIR = ROOT / "pipelines"

if str(PIPELINES_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINES_DIR))

from normalizers.jobs import (
    extract_skills,
    infer_remote_type,
    infer_seniority,
    normalize_greenhouse_job,
    parse_salary_range,
)


class JobNormalizerTests(unittest.TestCase):
    def test_infer_remote_type_from_location(self) -> None:
        self.assertEqual(infer_remote_type("Remote - US", ""), "remote")

    def test_infer_remote_type_uses_word_boundaries(self) -> None:
        self.assertEqual(infer_remote_type("Office", "remote-first team"), "remote")
        self.assertEqual(infer_remote_type("Office", "hybrid-friendly role"), "hybrid")

    def test_infer_seniority_for_staff_title(self) -> None:
        self.assertEqual(infer_seniority("Staff Data Engineer"), "senior")

    def test_infer_seniority_prioritizes_management(self) -> None:
        self.assertEqual(infer_seniority("Senior Engineering Manager"), "management")

    def test_parse_salary_range(self) -> None:
        self.assertEqual(parse_salary_range("$120,000 - $150,000 USD"), (120000, 150000, "USD"))
        self.assertEqual(parse_salary_range("Compensation: 90k - 110k"), (90000, 110000, None))

    def test_extract_skills(self) -> None:
        self.assertEqual(
            extract_skills("Build pipelines with Python, SQL, Docker, and Prefect."),
            ["Docker", "Prefect", "Python", "SQL"],
        )

    def test_normalize_greenhouse_job(self) -> None:
        raw_job = {
            "id": 123,
            "title": "Senior Backend Engineer",
            "content": "Build APIs for a remote team with Python, SQL, and Docker.",
            "absolute_url": "https://example.com/jobs/123",
            "updated_at": "2026-05-11T12:00:00Z",
            "location": {"name": "Remote - LATAM"},
            "metadata": [
                {"name": "Employment Type", "value": "Full-time"},
                {"name": "Salary Range", "value": "$120,000 - $150,000 USD"},
            ],
            "departments": [{"name": "Engineering"}],
        }

        normalized = normalize_greenhouse_job(raw_job, "demo-company")

        self.assertEqual(normalized["source"], "greenhouse")
        self.assertEqual(normalized["source_job_id"], "123")
        self.assertEqual(normalized["employment_type"], "Full-time")
        self.assertEqual(normalized["remote_type"], "remote")
        self.assertEqual(normalized["seniority"], "senior")
        self.assertEqual(normalized["department"], "Engineering")
        self.assertEqual(normalized["salary_min"], 120000)
        self.assertEqual(normalized["salary_max"], 150000)
        self.assertEqual(normalized["salary_currency"], "USD")
        self.assertEqual(normalized["skills"], ["Docker", "Python", "SQL"])


if __name__ == "__main__":
    unittest.main()
