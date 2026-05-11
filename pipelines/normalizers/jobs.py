import re
from datetime import datetime


CURRENCY_SYMBOLS = {
    "$": "USD",
}

SKILL_KEYWORDS = {
    "airflow": "Airflow",
    "aws": "AWS",
    "dbt": "dbt",
    "docker": "Docker",
    "fastapi": "FastAPI",
    "gcp": "GCP",
    "kubernetes": "Kubernetes",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "prefect": "Prefect",
    "python": "Python",
    "react": "React",
    "snowflake": "Snowflake",
    "spark": "Spark",
    "sql": "SQL",
    "terraform": "Terraform",
    "typescript": "TypeScript",
}


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    without_tags = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", without_tags).strip()


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def infer_remote_type(location_text: str | None, job_text: str) -> str | None:
    haystack = normalize_text(f"{location_text or ''} {job_text}").lower()
    if re.search(r"\bhybrid\b", haystack):
        return "hybrid"
    if re.search(r"\bremote\b|\bwork from home\b|\bwfh\b", haystack):
        return "remote"
    return "onsite" if location_text else None


def infer_seniority(title: str) -> str | None:
    lowered = title.lower()
    if re.search(r"\b(manager|director|head|vp|vice president)\b", lowered):
        return "management"
    if re.search(r"\b(senior|sr|staff|principal|lead)\b", lowered):
        return "senior"
    if re.search(r"\b(intern|junior|jr|associate|entry)\b", lowered):
        return "junior"
    return "mid"


def parse_salary_range(text: str | None) -> tuple[int | None, int | None, str | None]:
    if not text:
        return None, None, None

    compact = normalize_text(text).replace(",", "")
    currency = next((code for symbol, code in CURRENCY_SYMBOLS.items() if symbol in compact), None)
    if currency is None:
        match = re.search(r"\b(USD|EUR|GBP|CAD|AUD)\b", compact, flags=re.IGNORECASE)
        currency = match.group(1).upper() if match else None

    values = []
    for match in re.finditer(r"(?<!\w)(\d+(?:\.\d+)?)\s*([kK])?\b", compact):
        value = float(match.group(1))
        if match.group(2):
            value *= 1000
        if value >= 1000:
            values.append(int(value))

    if not values:
        return None, None, currency
    if len(values) == 1:
        return values[0], None, currency
    return min(values[:2]), max(values[:2]), currency


def extract_skills(text: str | None) -> list[str]:
    haystack = normalize_text(text).lower()
    skills = {
        label
        for keyword, label in SKILL_KEYWORDS.items()
        if re.search(rf"\b{re.escape(keyword)}\b", haystack)
    }
    return sorted(skills)


def normalize_greenhouse_job(job: dict, board_token: str) -> dict:
    content = job.get("content") or ""
    location = job.get("location") or {}
    metadata = job.get("metadata") or []

    employment_type = None
    salary_min = None
    salary_max = None
    salary_currency = None
    for item in metadata:
        name = (item.get("name") or "").lower()
        value = item.get("value")
        if "employment" in name or "type" == name:
            employment_type = value
        if any(token in name for token in ["salary", "compensation", "pay range"]):
            salary_min, salary_max, salary_currency = parse_salary_range(str(value))

    if salary_min is None and salary_max is None:
        salary_min, salary_max, salary_currency = parse_salary_range(content)

    searchable_text = " ".join(
        [
            job.get("title") or "",
            location.get("name") or "",
            content,
        ]
    )

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
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": salary_currency,
        "skills": extract_skills(searchable_text),
        "description_html": content,
        "apply_url": job.get("absolute_url"),
        "posting_url": job.get("absolute_url"),
        "published_at": parse_datetime(job.get("updated_at")),
        "is_active": True,
    }
