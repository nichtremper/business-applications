#!/usr/bin/env python3
"""
Standalone script: download all BFS data and save static HTML charts.

Usage:
    python download_and_chart.py --api-key YOUR_KEY --start 2006-01-01 --out charts/
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

from fred_biz_apps import BFSDownloader
from fred_biz_apps.charts import bar_chart_latest, time_series_chart, yoy_change_chart


def main() -> None:
    parser = argparse.ArgumentParser(description="Download FRED BFS data and create charts.")
    parser.add_argument("--api-key", default=os.environ.get("FRED_API_KEY", ""),
                        help="FRED API key (or set FRED_API_KEY env var)")
    parser.add_argument("--start", default="2006-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default=None, help="End date (YYYY-MM-DD)")
    parser.add_argument("--out", default="charts", help="Output directory for HTML charts")
    parser.add_argument("--cache", default="bfs_cache", help="Cache directory")
    args = parser.parse_args()

    if not args.api_key:
        parser.error("Provide --api-key or set FRED_API_KEY env var.")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    dl = BFSDownloader(api_key=args.api_key, cache_dir=args.cache)
    logging.info("Downloading data (start=%s, end=%s)…", args.start, args.end)
    data = dl.get_all(start=args.start, end=args.end)

    totals = data["totals"]
    ind_ba = data["industry_ba"]
    ind_hba = data["industry_hba"]

    charts = [
        (
            time_series_chart(totals, title="Total Business Applications Over Time"),
            "totals_level.html",
        ),
        (
            yoy_change_chart(totals, title="Total Business Applications – YoY % Change"),
            "totals_yoy.html",
        ),
        (
            time_series_chart(ind_ba, title="Business Applications by Industry"),
            "industry_ba_level.html",
        ),
        (
            yoy_change_chart(ind_ba, title="Business Applications by Industry – YoY % Change"),
            "industry_ba_yoy.html",
        ),
        (
            bar_chart_latest(ind_ba, title="Latest Business Applications by Industry"),
            "industry_ba_bar.html",
        ),
        (
            time_series_chart(ind_hba, title="High-Propensity Business Applications by Industry"),
            "industry_hba_level.html",
        ),
        (
            bar_chart_latest(ind_hba, title="Latest High-Propensity Business Applications by Industry"),
            "industry_hba_bar.html",
        ),
    ]

    for fig, fname in charts:
        path = out_dir / fname
        fig.write_html(str(path))
        logging.info("Saved %s", path)

    logging.info("Done. Open any .html file in your browser.")


if __name__ == "__main__":
    main()
