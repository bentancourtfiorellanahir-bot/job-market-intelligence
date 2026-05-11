import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINES_DIR = ROOT / "pipelines"

if str(PIPELINES_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINES_DIR))

from normalizers.jobs import infer_remote_type, infer_seniority, normalize_greenhouse_job


class JobNormalizerTests(unittest.TestCase):
    def test_infer_remote_type_from_location(self) -> None:
        self.assertEqual(infer_remote_type("Remote - US", ""), "remote")

    def test_infer_seniority_for_staff_title(self) -> None:
        self.assertEqual(infer_seniority("Staff Data Engineer"), "senior")

    def test_normalize_greenhouse_job(self) -> None:
        raw_job = {
            "id": 123,
            "title": "Senior Backend Engineer",
            "content": "Build APIs for a remote team.",
            "absolute_url": "https://example.com/jobs/123",
            "updated_at": "2026-05-11T12:00:00Z",
            "location": {"name": "Remote - LATAM"},
            "metadata": [{"name": "Employment Type", "value": "Full-time"}],
            "departments": [{"name": "Engineering"}],
        }

        normalized = normalize_greenhouse_job(raw_job, "demo-company")

        self.assertEqual(normalized["source"], "greenhouse")
        self.assertEqual(normalized["source_job_id"], "123")
        self.assertEqual(normalized["employment_type"], "Full-time")
        self.assertEqual(normalized["remote_type"], "remote")
        self.assertEqual(normalized["seniority"], "senior")
        self.assertEqual(normalized["department"], "Engineering")


if __name__ == "__main__":
    unittest.main()
