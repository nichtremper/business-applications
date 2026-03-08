"""
Low-level FRED REST API client.

All methods return Python dicts / lists (raw JSON). Higher-level helpers
live in downloader.py.
"""

from __future__ import annotations

import threading
import time
import logging
from typing import Any

import requests

FRED_BASE = "https://api.stlouisfed.org/fred"
logger = logging.getLogger(__name__)


class FREDClient:
    """Thin wrapper around the FRED HTTP API."""

    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self._local = threading.local()

    @property
    def _session(self) -> requests.Session:
        """Return a per-thread Session so concurrent fetches don't share state."""
        if not hasattr(self._local, "session"):
            self._local.session = requests.Session()
        return self._local.session

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, endpoint: str, params: dict[str, Any] | None = None,
             retries: int = 3) -> dict:
        url = f"{FRED_BASE}/{endpoint}"
        p = {"api_key": self.api_key, "file_type": "json"}
        if params:
            p.update(params)

        for attempt in range(retries):
            try:
                resp = self._session.get(url, params=p, timeout=self.timeout)
                resp.raise_for_status()
                return resp.json()
            except requests.HTTPError as exc:
                logger.warning("HTTP %s for %s (attempt %d/%d)",
                               exc.response.status_code, url, attempt + 1, retries)
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise
            except requests.RequestException as exc:
                logger.warning("Request error %s (attempt %d/%d)",
                               exc, attempt + 1, retries)
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def series_info(self, series_id: str) -> dict:
        """Metadata for a single series."""
        data = self._get("series", {"series_id": series_id})
        return data.get("seriess", [{}])[0]

    def series_observations(
        self,
        series_id: str,
        observation_start: str | None = None,
        observation_end: str | None = None,
        units: str = "lin",
    ) -> list[dict]:
        """Return list of {date, value} dicts for *series_id*."""
        params: dict[str, Any] = {"series_id": series_id, "units": units}
        if observation_start:
            params["observation_start"] = observation_start
        if observation_end:
            params["observation_end"] = observation_end
        data = self._get("series/observations", params)
        return data.get("observations", [])

    def search(self, query: str, limit: int = 1000) -> list[dict]:
        """Full-text search; returns list of series metadata dicts."""
        data = self._get(
            "series/search",
            {"search_text": query, "limit": limit},
        )
        return data.get("seriess", [])

    def category_series(self, category_id: int, limit: int = 1000) -> list[dict]:
        """All series in a FRED category."""
        data = self._get(
            "category/series",
            {"category_id": category_id, "limit": limit},
        )
        return data.get("seriess", [])
