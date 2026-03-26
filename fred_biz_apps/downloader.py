"""
BFSDownloader – downloads Business Formation Statistics from FRED and
optionally caches results locally as Parquet files.

Usage
-----
    from fred_biz_apps import BFSDownloader

    dl = BFSDownloader(api_key="YOUR_KEY", cache_dir="./bfs_cache")

    # All aggregate / total series
    totals = dl.get_totals(start="2004-01-01", end="2024-12-31")

    # All industry series (one column per industry, two sub-frames: ba / hba)
    industry_ba, industry_hba = dl.get_by_industry(start="2004-01-01")

    # Everything in one dict
    all_data = dl.get_all(start="2004-01-01")
"""

from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

import pandas as pd

from .catalog import (
    TOTAL_SERIES,
    INDUSTRY_SERIES,
    INDUSTRY_NAMES,
    EMPLOYMENT_SERIES,
)
from .client import FREDClient

logger = logging.getLogger(__name__)


class BFSDownloader:
    """Download and (optionally) cache FRED BFS series."""

    def __init__(
        self,
        api_key: str,
        cache_dir: str | Path | None = None,
        timeout: int = 30,
    ):
        self.client = FREDClient(api_key=api_key, timeout=timeout)
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def _cache_path(self, series_id: str) -> Path | None:
        if self.cache_dir is None:
            return None
        return self.cache_dir / f"{series_id}.parquet"

    def _load_cached(self, series_id: str) -> pd.DataFrame | None:
        path = self._cache_path(series_id)
        if path and path.exists():
            logger.debug("Cache hit: %s", series_id)
            return pd.read_parquet(path)
        return None

    def _save_cache(self, series_id: str, df: pd.DataFrame) -> None:
        path = self._cache_path(series_id)
        if path:
            df.to_parquet(path)

    def _fetch_series(
        self,
        series_id: str,
        start: str | None = None,
        end: str | None = None,
    ) -> pd.Series:
        """
        Fetch one FRED series, return a pandas Series indexed by date.
        Falls back gracefully if the series does not exist on FRED.
        """
        cached = self._load_cached(series_id)
        if cached is not None:
            s = cached["value"]
            s.index = pd.to_datetime(cached["date"])
            s.name = series_id
            # Slice to requested date range
            if start:
                s = s[s.index >= start]
            if end:
                s = s[s.index <= end]
            return s

        try:
            obs = self.client.series_observations(
                series_id,
                observation_start=start,
                observation_end=end,
            )
        except Exception as exc:
            logger.warning("Could not fetch %s: %s", series_id, exc)
            return pd.Series(name=series_id, dtype=float)

        if not obs:
            return pd.Series(name=series_id, dtype=float)

        df_raw = pd.DataFrame(obs)
        df_raw["date"] = pd.to_datetime(df_raw["date"])
        df_raw["value"] = pd.to_numeric(df_raw["value"], errors="coerce")
        df_raw = df_raw.set_index("date")

        # Save full (unsliced) for cache, then slice for caller
        if self.cache_dir:
            save_df = df_raw.reset_index()[["date", "value"]]
            self._save_cache(series_id, save_df)

        s = df_raw["value"]
        s.name = series_id
        return s

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_totals(
        self,
        start: str | None = None,
        end: str | None = None,
    ) -> pd.DataFrame:
        """
        Download all aggregate (total / national) BFS series.

        Returns a wide DataFrame where each column is one series, indexed by date.
        The column names are human-readable labels (not raw FRED IDs).
        """
        def _fetch(item):
            sid, meta = item
            logger.info("Fetching %s …", sid)
            return meta["label"], self._fetch_series(sid, start=start, end=end)

        frames: dict[str, pd.Series] = {}
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = {pool.submit(_fetch, item): item for item in TOTAL_SERIES.items()}
            for future in as_completed(futures):
                label, s = future.result()
                if not s.empty:
                    frames[label] = s

        if not frames:
            return pd.DataFrame()
        df = pd.DataFrame(frames)
        df.index.name = "date"
        return df

    def get_by_industry(
        self,
        start: str | None = None,
        end: str | None = None,
        series_type: str = "ba",  # "ba" | "hba" | "both"
    ) -> pd.DataFrame | tuple[pd.DataFrame, pd.DataFrame]:
        """
        Download industry-level BFS series.

        Parameters
        ----------
        start, end : str
            Date strings in 'YYYY-MM-DD' format.
        series_type : "ba" | "hba" | "both"
            Which set to download.  "both" returns a tuple (ba_df, hba_df).

        Returns
        -------
        DataFrame(s) with industry names as columns, indexed by date.
        """
        ba_frames: dict[str, pd.Series] = {}
        hba_frames: dict[str, pd.Series] = {}

        # Build list of (kind, industry, series_id) tasks to run in parallel
        tasks: list[tuple[str, str, str]] = []
        for industry, ids in INDUSTRY_SERIES.items():
            if series_type in ("ba", "both"):
                tasks.append(("ba", industry, ids["ba_id"]))
            if series_type in ("hba", "both"):
                tasks.append(("hba", industry, ids["hba_id"]))

        def _fetch(kind: str, industry: str, sid: str):
            logger.info("Fetching %s %s …", kind.upper(), sid)
            return kind, industry, self._fetch_series(sid, start=start, end=end)

        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = {pool.submit(_fetch, *t): t for t in tasks}
            for future in as_completed(futures):
                kind, industry, s = future.result()
                if not s.empty:
                    if kind == "ba":
                        ba_frames[industry] = s
                    else:
                        hba_frames[industry] = s

        def _build(frames: dict) -> pd.DataFrame:
            if not frames:
                return pd.DataFrame()
            df = pd.DataFrame(frames)
            df.index.name = "date"
            return df

        if series_type == "ba":
            return _build(ba_frames)
        if series_type == "hba":
            return _build(hba_frames)
        return _build(ba_frames), _build(hba_frames)

    def get_all(
        self,
        start: str | None = None,
        end: str | None = None,
    ) -> dict[str, pd.DataFrame]:
        """
        Convenience method – returns a dict with keys:
            "totals"       : aggregate series DataFrame
            "industry_ba"  : industry business applications DataFrame
            "industry_hba" : industry high-propensity DataFrame
        """
        totals = self.get_totals(start=start, end=end)
        industry_ba, industry_hba = self.get_by_industry(
            start=start, end=end, series_type="both"
        )
        return {
            "totals": totals,
            "industry_ba": industry_ba,
            "industry_hba": industry_hba,
        }

    def get_employment(
        self,
        start: str | None = None,
        end: str | None = None,
    ) -> pd.DataFrame:
        """
        Fetch CES employment series for all industries that have normalization data.

        Returns a wide DataFrame keyed by FRED series ID (e.g. ``MANEMP``,
        ``CES5552000001``), indexed by date.  Values are thousands of persons,
        seasonally adjusted, as reported by BLS via FRED.
        """
        unique_ids = {sid for sid in EMPLOYMENT_SERIES.values() if sid is not None}

        frames: dict[str, pd.Series] = {}

        def _fetch(sid: str):
            logger.info("Fetching employment series %s …", sid)
            return sid, self._fetch_series(sid, start=start, end=end)

        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = {pool.submit(_fetch, sid): sid for sid in unique_ids}
            for future in as_completed(futures):
                sid, s = future.result()
                if not s.empty:
                    frames[sid] = s

        if not frames:
            return pd.DataFrame()
        df = pd.DataFrame(frames)
        df.index.name = "date"
        return df

    def get_normalized_rates(
        self,
        start: str | None = None,
        end: str | None = None,
        series_type: str = "ba",  # "ba" | "hba"
    ) -> pd.DataFrame:
        """
        Business applications per 10,000 workers for each industry.

        Employment series (from BLS CES via FRED) are in thousands of persons.
        The rate formula accounts for that unit:

            rate = BA_count / (employment_thousands × 1,000) × 10,000
                 = BA_count × 10 / employment_thousands

        Agriculture (NAICS 11) is excluded because the CES nonfarm payroll
        survey does not cover agricultural workers.

        Parameters
        ----------
        series_type : "ba" | "hba"
            Which business-application series to normalize.

        Returns
        -------
        DataFrame with one column per industry (18 max), indexed by date.
        Values are applications per 10,000 workers.
        """
        ba_df = self.get_by_industry(start=start, end=end, series_type=series_type)
        emp_df = self.get_employment(start=start, end=end)

        if ba_df.empty or emp_df.empty:
            return pd.DataFrame()

        rate_frames: dict[str, pd.Series] = {}

        for industry, emp_sid in EMPLOYMENT_SERIES.items():
            if emp_sid is None:
                # Agriculture – no CES employment coverage
                continue
            if industry not in ba_df.columns:
                logger.warning(
                    "No %s data for '%s'; skipping normalization.", series_type.upper(), industry
                )
                continue
            if emp_sid not in emp_df.columns:
                logger.warning(
                    "Employment series %s not available for '%s'; skipping.", emp_sid, industry
                )
                continue

            ba = ba_df[industry].copy()
            emp = emp_df[emp_sid].copy()

            # Align on calendar month – both series are monthly but may be
            # stamped to different days-of-month by FRED.
            ba.index = pd.to_datetime(ba.index).to_period("M")
            emp.index = pd.to_datetime(emp.index).to_period("M")

            aligned = pd.DataFrame({"ba": ba, "emp": emp}).dropna()
            if aligned.empty:
                logger.warning("No overlapping dates for '%s'; skipping.", industry)
                continue

            # Employment in thousands → total workers = emp × 1,000
            # apps per 10,000 workers = BA / (emp × 1,000) × 10,000
            #                         = BA × 10 / emp
            rate = aligned["ba"] * 10.0 / aligned["emp"]
            rate.index = rate.index.to_timestamp()
            rate.name = industry
            rate_frames[industry] = rate

        if not rate_frames:
            return pd.DataFrame()

        result = pd.DataFrame(rate_frames)
        result.index.name = "date"
        return result

    def refresh_cache(self) -> None:
        """Delete cached files and re-download everything."""
        if self.cache_dir:
            for f in self.cache_dir.glob("*.parquet"):
                f.unlink()
            logger.info("Cache cleared.")
        else:
            logger.warning("No cache_dir configured; nothing to clear.")
