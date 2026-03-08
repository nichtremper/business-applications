# fred-biz-apps

A Python package + Shiny for Python app that downloads **FRED Business Formation
Statistics (BFS)** data from the St. Louis Fed and visualises it interactively.

---

## What data is included?

All data comes from the **U.S. Census Bureau Business Formation Statistics**,
mirrored on FRED:

| Category | Series | Notes |
|---|---|---|
| Total business applications | `BABATOTALSAUS` | Weekly, NSA |
| Total – 4-week moving avg | `BABATOTALMAVG4SAUS` | Weekly, NSA |
| Total – seasonally adjusted | `BABATOTALSASAUS` | SA annual rate |
| High-propensity applications | `HBABATOTALSAUS` | Weekly, NSA |
| High-propensity – 4-week MA | `HBABATOTALMAVG4SAUS` | Weekly, NSA |
| High-propensity – SA | `HBABATOTALSASAUS` | SA annual rate |
| Industry breakdown (×20 NAICS sectors) | `BABAnnNQNSA` / `HBABAnnNQNSA` | Quarterly, NSA |

High-propensity = applications with a high likelihood of becoming an employer
business (uses EIN, wages, third-party payroll).

---

## Quick start

### 1. Install

```bash
pip install -e .
# or, without editable install:
pip install -r requirements.txt
```

> Python 3.10+ required.

### 2. Run the Shiny app

```bash
shiny run app.py
```

Then open **http://localhost:8000** in your browser, paste your FRED API key
in the sidebar, and click **Fetch / Refresh Data**.

### 3. Use as a Python library

```python
from fred_biz_apps import BFSDownloader

dl = BFSDownloader(
    api_key="YOUR_FRED_API_KEY",
    cache_dir="bfs_cache",   # omit to disable local caching
)

# All aggregate series as a single wide DataFrame
totals = dl.get_totals(start="2010-01-01")

# Industry-level, just business applications
industry_ba = dl.get_by_industry(series_type="ba")

# Industry-level, just high-propensity
industry_hba = dl.get_by_industry(series_type="hba")

# Everything at once
data = dl.get_all(start="2006-01-01")
# data["totals"], data["industry_ba"], data["industry_hba"]
```

### 4. Generate static HTML charts (no Shiny needed)

```bash
python download_and_chart.py --api-key YOUR_KEY --start 2006-01-01 --out charts/
# Opens each .html file in any browser
```

---

## Shiny app features

| Feature | Detail |
|---|---|
| Date range picker | Any start + end date |
| Totals tab | Choose any combination of the 6 aggregate series |
| Industry tab | Select **All** or N specific industries via multi-select text search |
| Series type | Toggle between Business Applications and High-Propensity |
| Chart type | Level or Year-over-Year % Change |
| Bar chart | Latest 4-period average across industries |
| Data table | Filtered, formatted table of the active dataset |
| Full-screen | Each chart card has a full-screen button |
| Caching | Data cached locally as Parquet; click Refresh to re-download |

---

## Admin / setup tasks you need to do

### A. Get a FRED API Key (free, 2 minutes)

1. Go to <https://fredaccount.stlouisfed.org/login/secure/>
2. Create a free account (or log in).
3. Under **My Account → API Keys**, request a new key.
4. Copy the key — it looks like `03de7b9f3cc1a2e003e5b7fee40f5774`.

You can pass it at runtime (via the sidebar) or set it once as an environment
variable so the app pre-fills:

```bash
export FRED_API_KEY="03de7b9f3cc1a2e003e5b7fee40f5774"
shiny run app.py
```

### B. Python environment

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### C. (Optional) Deploy to shinyapps.io

1. Install rsconnect-python:
   ```bash
   pip install rsconnect-python
   ```
2. Authorise:
   ```bash
   rsconnect add --account YOUR_ACCOUNT --name shinyapps --token TOKEN --secret SECRET
   ```
   (Tokens are in your shinyapps.io dashboard → Account → Tokens)
3. Deploy:
   ```bash
   rsconnect deploy shiny . --name shinyapps --title "FRED Business Applications"
   ```
4. Set the `FRED_API_KEY` environment variable inside the shinyapps.io dashboard
   (Apps → your-app → Vars) so users don't need to type the key.

### D. (Optional) Deploy to Posit Connect / your own server

```bash
# Posit Connect
rsconnect deploy shiny . --server https://your-connect-server --api-key CONNECT_KEY
```

For any self-hosted deployment, set `FRED_API_KEY` as a server environment
variable and the sidebar will pre-populate automatically.

---

## Project layout

```
business-applications/
├── fred_biz_apps/
│   ├── __init__.py       # public API
│   ├── client.py         # thin FRED HTTP client
│   ├── catalog.py        # all known series IDs & metadata
│   ├── downloader.py     # BFSDownloader (fetch + cache)
│   └── charts.py         # Plotly chart helpers
├── app.py                # Shiny for Python app
├── download_and_chart.py # standalone CLI script
├── requirements.txt
└── pyproject.toml
```

---

## Notes on data availability

* Industry-level series are **quarterly and not seasonally adjusted**.
  The aggregate (total) series also come in weekly and seasonally-adjusted forms.
* FRED series availability may change over time. If a series returns no data
  the downloader silently skips it.
* Data typically has a ~2-week lag from the current date.
