from abc import ABC, abstractmethod
import httpx
import asyncio
import time

# Simple module-level rate limiter to serialize requests and avoid API rate-limits.
# Adjust `RATE_LIMIT_DELAY` as needed (seconds between requests).
RATE_LIMIT_DELAY = 0.25
_rate_lock = asyncio.Lock()
_last_request_at = 0.0


class BaseExtractor(ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def fetch_raw_data(self, endpoint: str, params: dict = None):
        """
        Fetch JSON from the API with a global async lock and simple retry/backoff.

        This serializes requests across the process to avoid hitting API rate limits
        when multiple concurrent tasks are running.
        """
        global _last_request_at

        retries = 3
        base_backoff = 0.8

        for attempt in range(1, retries + 1):
            try:
                async with _rate_lock:
                    # enforce minimum delay between requests
                    now = time.time()
                    wait = RATE_LIMIT_DELAY - (now - _last_request_at)
                    if wait > 0:
                        await asyncio.sleep(wait)

                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{self.base_url}{endpoint}", params=params, timeout=30.0)
                        _last_request_at = time.time()

                    # if server indicates temporary overload, raise to trigger retry/backoff
                    if response.status_code in (429, 500, 502, 503, 504):
                        response.raise_for_status()

                    return response.json()

            except httpx.HTTPStatusError as he:
                # server returned an error status code; retry a few times with backoff
                if attempt < retries:
                    await asyncio.sleep(base_backoff * attempt)
                    continue
                raise
            except (httpx.RequestError, asyncio.TimeoutError) as re:
                # network-level error; retry
                if attempt < retries:
                    await asyncio.sleep(base_backoff * attempt)
                    continue
                raise

    @abstractmethod
    def parse_schema(self, data: dict):
        pass
