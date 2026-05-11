import httpx


class GreenhouseConnector:
    BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

    def __init__(self, board_token: str) -> None:
        self.board_token = board_token

    def fetch_jobs(self) -> list[dict]:
        url = f"{self.BASE_URL}/{self.board_token}/jobs"
        response = httpx.get(url, params={"content": "true"}, timeout=30.0)
        response.raise_for_status()
        payload = response.json()
        return payload.get("jobs", [])

