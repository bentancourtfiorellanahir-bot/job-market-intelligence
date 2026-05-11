import time

import httpx


class GreenhouseConnector:
    BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

    def __init__(
        self,
        board_token: str,
        timeout_seconds: float = 30.0,
        max_attempts: int = 3,
        backoff_seconds: float = 1.0,
    ) -> None:
        self.board_token = board_token
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds

    def fetch_jobs(self) -> list[dict]:
        url = f"{self.BASE_URL}/{self.board_token}/jobs"
        last_error: httpx.HTTPError | None = None
        with httpx.Client(timeout=self.timeout_seconds) as client:
            for attempt in range(1, self.max_attempts + 1):
                try:
                    response = client.get(url, params={"content": "true"})
                    response.raise_for_status()
                    payload = response.json()
                    return payload.get("jobs", [])
                except httpx.HTTPError as exc:
                    last_error = exc
                    if attempt == self.max_attempts:
                        break
                    time.sleep(self.backoff_seconds * attempt)

        message = f"Failed to fetch Greenhouse jobs for board '{self.board_token}'"
        raise RuntimeError(message) from last_error
