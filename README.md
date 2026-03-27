# fred-biz-apps

A Python package and interactive Shiny dashboard that wraps the **FRED Business
Formation Statistics (BFS)** — monthly data on new business applications and
high-propensity business applications published by the U.S. Census Bureau and
hosted by the Federal Reserve Bank of St. Louis.

> **A FRED API key is required.** It is free and takes about two minutes to
> obtain — see [Get a FRED API key](#1-get-a-fred-api-key-required) below.

---

## What data is included?

All series come from the **U.S. Census Bureau Business Formation Statistics**,
accessed via the [FRED API](https://fred.stlouisfed.org/).

### Aggregate (national totals) — monthly

| Series ID | Description | Adj |
|---|---|---|
| `BABATOTALSAUS` | Total Business Applications | SA |
| `BABATOTALNSAUS` | Total Business Applications | NSA |
| `BAHBATOTALSAUS` | High-Propensity Business Applications | SA |
| `BAHBATOTALNSAUS` | High-Propensity Business Applications | NSA |

**Business Applications (BA)** count all EIN applications filed with the IRS,
excluding certain low-transition-rate categories (agriculture, public
administration, private households, civic organisations).

**High-Propensity Business Applications (HBA)** are the subset of BA that have
a high likelihood of becoming an employer business — typically those from a
corporate entity, indicating planned wages, or operating in sectors with high
formation rates (manufacturing, retail, health care, food service).

### Industry-level — monthly, by NAICS sector

Covers 19 NAICS sectors (e.g. Construction, Finance & Insurance, Health Care,
Retail Trade). Each sector has a BA series and an HBA series, in either
seasonally adjusted or not-seasonally-adjusted form depending on availability.

---

## Quick start

### 1. Get a FRED API key (required)

A FRED API key is **required** to download any data. The key is free:

1. Go to <https://fredaccount.stlouisfed.org/login/secure/>
2. Create a free account (or sign in to an existing one).
3. Navigate to **My Account → API Keys** and click **Request API Key**.
4. Copy the key.

You can enter the key in the app sidebar each time, or set it as an environment
variable so the app pre-fills it automatically:

```bash
export FRED_API_KEY="your_key_here"
```

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> Python 3.10+ required.

### 3. Launch the Shiny app

```bash
shiny run app.py
```

Then open **http://localhost:8000** in your browser.

1. Paste your FRED API key into the **FRED API Key** field in the left sidebar.
2. Click **Fetch / Refresh Data**.
3. Once data loads, explore the **Totals**, **By Industry**, and **Data Table** tabs.

To pre-fill the key automatically, set the environment variable before running:

```bash
FRED_API_KEY="your_key_here" shiny run app.py
```

---

## App features

| Feature | Detail |
|---|---|
| **Totals tab** | Time-series chart of the four national aggregate series with a configurable series filter |
| **By Industry tab** | Multi-select industries; choose "All" to overlay national totals, or pick specific NAICS sectors |
| **Apps per Worker tab** | Business applications per 10,000 workers by industry — normalized for sector size to enable entrepreneurship comparisons; includes a **Download CSV** button |
| **Series type** | Toggle between Business Applications and High-Propensity Business Applications |
| **Chart type** | Level, Year-over-Year % Change, or Indexed (normalized to a user-selected base period) |
| **3-month MA overlay** | Optional moving-average line on level charts |
| **Date range** | Configurable start and end date applied across all views |
| **Data Table tab** | Filterable table of the active dataset with a **Download CSV** button |
| **Full-screen** | Each chart card can be expanded to full-screen |
| **Local cache** | Data is cached as Parquet files in `bfs_cache/`; click Refresh to re-download |

---

## Apps per Worker — methodology and reconciliation

The **Apps per Worker** tab normalizes business application counts by total
employment in each industry, producing a rate that makes large and small
sectors directly comparable.

### Rate formula

Employment series from BLS CES are reported in **thousands of persons**.
The rate is expressed as **applications per 10,000 workers**:

```
rate = BA_count × 10 / employment_thousands
```

*Equivalently: `BA_count / (employment_thousands × 1,000) × 10,000`.*

### Employment series used

| Industry (NAICS) | FRED Employment Series | Notes |
|---|---|---|
| Agriculture, Forestry, Fishing & Hunting (11) | — | Excluded — see below |
| Mining, Quarrying & Oil and Gas Extraction (21) | `USMINE` | See below |
| Utilities (22) | `USUTIL` | Clean match |
| Construction (23) | `USCONS` | Clean match |
| Manufacturing (31–33) | `MANEMP` | Clean match |
| Wholesale Trade (42) | `CES4142000001` | Clean match |
| Retail Trade (44–45) | `USTRADE` | Clean match |
| Transportation & Warehousing (48–49) | `CES4300000001` | Clean match |
| Information (51) | `USINFO` | Clean match |
| Finance & Insurance (52) | `CES5552000001` | Clean match |
| Real Estate & Rental and Leasing (53) | `CES5553000001` | Clean match |
| Professional, Scientific & Technical Services (54) | `CES6054000001` | Clean match |
| Management of Companies & Enterprises (55) | `CES6055000001` | Clean match |
| Administrative & Support / Waste Management (56) | `CES6056000001` | Clean match |
| Educational Services (61) | `CES6561000001` | See below |
| Health Care & Social Assistance (62) | `CES6562000001` | Clean match |
| Arts, Entertainment & Recreation (71) | `CES7071000001` | Clean match |
| Accommodation & Food Services (72) | `CES7072000001` | Clean match |
| Other Services excl. Public Administration (81) | `USSERV` | Clean match |

All employment series are from the **BLS Current Employment Statistics (CES)**
establishment survey — seasonally adjusted, all employees, monthly, in
thousands of persons.

### Reconciliation decisions

Three industries required reconciliation. Each decision is noted in
`catalog.py` and annotated on the relevant chart.

---

**Agriculture (NAICS 11) — excluded**

The CES is a *nonfarm* payroll survey. Agricultural workers are excluded
from CES by definition, so there is no meaningful employment denominator
for this sector. Business application data for Agriculture is available
in the Totals and By Industry tabs but does not appear in the Apps per
Worker tab.

---

**Mining, Quarrying & Oil and Gas Extraction (NAICS 21) — `USMINE`**

`USMINE` = *"All Employees: Mining and Logging"* — a BLS super-sector that
bundles NAICS 21 (mining) with logging, which is technically part of
NAICS 11 (Agriculture, Forestry, Fishing & Hunting). A more granular
mining-only series exists within the CES microdata but is not published
as a standalone FRED series.

**Effect:** the employment denominator is slightly too large (logging
workers are included), making the normalized rate slightly lower than the
true figure. The bias is small in practice — logging employment is a
minor share of the combined series.

---

**Educational Services (NAICS 61) — `CES6561000001` (private sector only)**

`CES6561000001` = *"All Employees: Private Educational Services"*. The
CES establishment survey separates private and government employment;
public-sector education workers (K-12 teachers, state university faculty,
community college staff, etc.) are classified under government and do not
appear in this series.

NAICS 61 covers *all* educational services — public and private — so the
business application numerator includes organizations across both sectors
while the employment denominator covers private-sector workers only.

**Effect:** the denominator understates true education-sector employment,
causing the normalized rate to be **overstated** for this industry. A
dagger (†) annotation is shown on every Apps per Worker chart as a
reminder. Comparisons involving Educational Services should be treated
with caution.

---

### Why these series and not the super-sectors?

Several BLS super-sectors combine multiple NAICS codes that are tracked
separately in the BFS data — for example, *Financial Activities*
(`USFIRE`) bundles Finance & Insurance (52) with Real Estate (53), and
*Professional and Business Services* (`USPBS`) bundles NAICS 54, 55,
and 56. Using a super-sector as the denominator for one of its
constituent industries would introduce a systematic bias: applications
in one sub-sector would be divided by the employment of the combined
sector, making all sub-sector rates artificially low.

FRED publishes granular CES sector-level series for each of these
industries individually (e.g. `CES5552000001` for Finance & Insurance,
`CES5553000001` for Real Estate). These are used throughout so that each
industry's rate reflects only that industry's own workforce.

---

## Use as a Python library

```python
from fred_biz_apps import BFSDownloader

dl = BFSDownloader(
    api_key="your_key_here",
    cache_dir="bfs_cache",   # omit to disable caching
)

# National totals as a wide DataFrame (date index, one column per series)
totals = dl.get_totals(start="2010-01-01")

# Industry-level business applications
industry_ba = dl.get_by_industry(series_type="ba")

# Industry-level high-propensity
industry_hba = dl.get_by_industry(series_type="hba")

# All datasets at once
data = dl.get_all(start="2006-01-01")
# data["totals"], data["industry_ba"], data["industry_hba"]

# Employment series (BLS CES, thousands of persons, SA)
emp = dl.get_employment(start="2006-01-01")

# Apps per 10,000 workers — one column per industry, 18 industries
rates_ba  = dl.get_normalized_rates(series_type="ba")
rates_hba = dl.get_normalized_rates(series_type="hba")
```

---

## Generate static HTML charts (no Shiny)

```bash
python download_and_chart.py --api-key your_key_here --start 2006-01-01 --out charts/
```

Each output `.html` file opens in any browser with no server required.

---

## Deployment

### shinyapps.io

```bash
pip install rsconnect-python
rsconnect add --account YOUR_ACCOUNT --name shinyapps --token TOKEN --secret SECRET
rsconnect deploy shiny . --name shinyapps --title "FRED Business Applications"
```

Set `FRED_API_KEY` in your app's environment variables (Apps → your-app → Vars)
so users don't need to enter the key manually.

### Posit Connect / self-hosted

```bash
rsconnect deploy shiny . --server https://your-connect-server --api-key CONNECT_KEY
```

Set `FRED_API_KEY` as a server environment variable and the sidebar will
pre-populate automatically.

---

## Project layout

```
business-applications/
├── fred_biz_apps/
│   ├── __init__.py       # public API
│   ├── client.py         # FRED HTTP client
│   ├── catalog.py        # all series IDs and metadata
│   ├── downloader.py     # BFSDownloader (fetch + cache)
│   └── charts.py         # Plotly chart helpers
├── app.py                # Shiny for Python dashboard
├── download_and_chart.py # standalone CLI script
├── requirements.txt
└── pyproject.toml
```

---

## Known issues

- **Charts may not render after the initial data fetch.** If the Totals or
  By Industry chart appears blank after clicking **Fetch / Refresh Data**,
  toggle one of the checkboxes under **Series to Display** in the sidebar
  (uncheck then re-check any item). This forces the chart to redraw. This is
  a known bug and will be fixed in a future release.

---

## Notes

- Data typically lags the current date by ~2 weeks.
- If a FRED series returns no data (e.g. a sector with limited availability),
  the downloader silently skips it rather than raising an error.
- All series are monthly and national (United States).
- Source: [U.S. Census Bureau Business Formation Statistics](https://www.census.gov/econ/bfs/index.html)
  via [FRED, Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/).
