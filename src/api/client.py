import time
from typing import Any

import requests
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.config import config

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class RetryableHTTPError(Exception):
    pass


class HTTPClient:
    def __init__(self) -> None:
        self._session = requests.Session()
        self._base_url = config.BASE_URL.rstrip("/")
        self._token = config.API_TOKEN
        self._timeout = config.REQUEST_TIMEOUT

    def _build_url(self, endpoint: str) -> str:
        return f"{self._base_url}/wrapi/{endpoint}/{self._token}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type(
            (requests.Timeout, requests.ConnectionError, RetryableHTTPError)
        ),
        reraise=True,
        before_sleep=lambda retry_state: logger.warning(
            f"Tentativa {retry_state.attempt_number} falhou, aguardando retry..."
        ),
    )
    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = self._build_url(endpoint)
        logger.debug(f"GET {endpoint} params={params}")

        response = self._session.get(url, params=params, timeout=self._timeout)

        if response.status_code in RETRYABLE_STATUS_CODES:
            wait_seconds = 30 if response.status_code == 429 else 0
            if wait_seconds:
                logger.warning(f"HTTP {response.status_code} em {endpoint}, aguardando {wait_seconds}s")
                time.sleep(wait_seconds)
            raise RetryableHTTPError(
                f"HTTP {response.status_code} em {endpoint}"
            )

        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._session.close()
