# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Set up environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the Shiny dashboard
shiny run app.py

# Generate static HTML charts (no Shiny required)
python download_and_chart.py --api-key YOUR_KEY --start 2006-01-01 --out charts/

# Run tests
pytest
```

## Architecture

This project downloads U.S. Census Bureau Business Formation Statistics (BFS) from the FRED API and displays them as an interactive Shiny for Python dashboard.

### `fred_biz_apps/` — Core library

- **`catalog.py`** — Master registry of all FRED series IDs: 4 national aggregate series (BA/HBA × seasonally adjusted/not), 19 NAICS industry sectors (BA/HBA variants each), and 18 BLS employment series for normalization.
- **`client.py`** — Thread-safe FRED HTTP API wrapper with retry logic.
- **`downloader.py`** — `BFSDownloader` fetches series concurrently (ThreadPoolExecutor), caches results as Parquet files in `bfs_cache/`, and handles transformation.
- **`charts.py`** — Reusable Plotly chart builders (level, YoY % change, indexed) with stable industry color mapping shared across all views.

### `app.py` — Shiny dashboard

Four tabs: **Totals** (national aggregates), **By Industry** (multi-select with overlay), **Apps per Worker** (normalized per 10,000 workers, CSV export), **Data Table** (filterable raw data, CSV download). Sidebar controls: API key, date range, chart type, moving average, index base date, full-screen toggle.

### Apps per Worker methodology

BLS CES employment series are matched to NAICS sectors with three special cases:
- Agriculture is excluded (no reliable BLS series)
- Mining uses the super-sector series
- Education uses the private-sector-only series

