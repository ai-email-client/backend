import requests
import json
import urllib3
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.schemas.request import OverviewRequest, WritterRequest
from config import Config
from app.schemas.response import DifySummaryResponse, OverviewResponse

logger = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def _log_response(response: requests.Response, *args, **kwargs):
    retry_count = response.request.headers.get("X-Retry-Count", 0)
    status = "✓" if response.ok else "✗"
    log_fn = logger.info if response.ok else logger.warning
    log_fn(
        f"[Dify] {status} {response.request.method} {response.url} "
        f"→ {response.status_code} (attempt {int(retry_count) + 1})"
    )

dify_session = requests.Session()
dify_session.mount("http://",  HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
dify_session.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
dify_session.hooks["response"].append(_log_response)


class DifyAPI:
    def __init__(self, config: Config):
        self.config = config

    def _post(self, api_key: str, payload: dict) -> DifySummaryResponse | None:
        url = self.config.DIFY_URL
        if not url:
            raise ValueError("Dify URL is not configured")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true",
        }
        try:
            response = dify_session.post(
                url=url,
                headers=headers,
                json=payload,
                verify=False,
                timeout=(1, 500),
            )
            response.raise_for_status()
            return DifySummaryResponse(**response.json())
        except Exception as e:
            logger.error(f"[Dify] Request failed: {e}")
            return None

    def _summary_payload(self, plain_text: str) -> dict:
        return {
            "inputs": {"email_text": plain_text[:4000]},
            "response_mode": "blocking",
            "user": "frontend-test",
        }

    def get_summary(self, plain_text: str) -> DifySummaryResponse | None:
        return self._post(self.config.DIFY_SUMMARY, self._summary_payload(plain_text))

    def test_summary(self, plain_text: str) -> DifySummaryResponse | None:
        return self._post(self.config.DIFY_SUMMARY, self._summary_payload(plain_text))

    def get_writter(self, req: WritterRequest) -> DifySummaryResponse | dict:
        payload = {
            "inputs": json.loads(req.model_dump_json()),
            "response_mode": "blocking",
            "user": "frontend-test",
        }
        result = self._post(self.config.DIFY_WRITER, payload)
        return result or {"error": "Request failed", "status": "failed"}

    def get_overview(self, req: OverviewRequest) -> DifySummaryResponse | None:
        payload = {
            "inputs": req.model_dump(),
            "response_mode": "blocking",
            "user": "frontend-test",
        }
        return self._post(self.config.DIFY_OVERVIEW, payload)