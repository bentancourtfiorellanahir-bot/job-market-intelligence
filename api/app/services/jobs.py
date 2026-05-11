from sqlalchemy.orm import Session

from app.repositories.jobs import JobRepository


class JobService:
    def __init__(self, db: Session) -> None:
        self.repository = JobRepository(db)

    def list_jobs(self, source: str | None = None, limit: int = 50):
        return self.repository.list_jobs(source=source, limit=limit)

