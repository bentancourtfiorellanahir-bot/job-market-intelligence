from datetime import datetime


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def infer_remote_type(location_text: str | None, job_text: str) -> str | None:
    haystack = f"{location_text or ''} {job_text}".lower()
    if "remote" in haystack:
        return "remote"
    if "hybrid" in haystack:
        return "hybrid"
    return "onsite" if location_text else None


def infer_seniority(title: str) -> str | None:
    lowered = title.lower()
    if any(token in lowered for token in ["senior", "staff", "principal", "lead"]):
        return "senior"
    if any(token in lowered for token in ["manager", "director", "head", "vp"]):
        return "management"
    if any(token in lowered for token in ["intern", "junior", "associate", "entry"]):
        return "junior"
    return "mid"


def normalize_greenhouse_job(job: dict, board_token: str) -> dict:
    content = job.get("content") or ""
    location = job.get("location") or {}
    metadata = job.get("metadata") or []

    employment_type = None
    for item in metadata:
        name = (item.get("name") or "").lower()
        if "employment" in name or "type" == name:
            employment_type = item.get("value")
            break

    return {
        "source": "greenhouse",
        "source_job_id": str(job["id"]),
        "board_token": board_token,
        "title": job["title"],
        "company_name": board_token,
        "department": (job.get("departments") or [{}])[0].get("name"),
        "location_text": location.get("name"),
        "employment_type": employment_type,
        "remote_type": infer_remote_type(location.get("name"), content),
        "seniority": infer_seniority(job["title"]),
        "salary_min": None,
        "salary_max": None,
        "salary_currency": None,
        "description_html": content,
        "apply_url": job.get("absolute_url"),
        "posting_url": job.get("absolute_url"),
        "published_at": parse_datetime(job.get("updated_at")),
        "is_active": True,
    }

