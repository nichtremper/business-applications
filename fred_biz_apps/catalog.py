"""
Catalog of FRED Business Formation Statistics (BFS) series.

The Census Bureau releases BFS data weekly (business applications) and
quarterly (seasonally-adjusted versions and high-propensity counts).
FRED mirrors all of them.

Series-ID naming convention used by FRED/Census:
    BABA   = Business Application, Business Applications
    HBABA  = High-propensity Business Application, Business Applications
    TOTALS = Total (all industries)
    <NN>   = 2-digit NAICS sector code
    A/NQ   = Annually / Not Quarterly
    SA/NSA = Seasonally Adjusted / Not Seasonally Adjusted
    US     = United States

We keep two parallel dictionaries:
    TOTAL_SERIES   – aggregate / "all industries" series
    INDUSTRY_SERIES – dict keyed by human-readable industry name,
                      each value is a dict with 'ba' and 'hba' keys
                      (business apps / high-propensity business apps)
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Aggregate / "Total" series
# ---------------------------------------------------------------------------

TOTAL_SERIES: dict[str, dict] = {
    # Weekly, not seasonally adjusted
    "BABATOTALSAUS": {
        "label": "Total Business Applications (Weekly, NSA)",
        "type": "ba",
        "frequency": "weekly",
        "seasonal_adj": False,
        "description": "Total business applications filed with the IRS, United States.",
    },
    # Weekly 4-week moving average, NSA
    "BABATOTALMAVG4SAUS": {
        "label": "Total Business Applications – 4-Week Moving Avg (NSA)",
        "type": "ba",
        "frequency": "weekly",
        "seasonal_adj": False,
        "description": "4-week moving average of total business applications.",
    },
    # Seasonally adjusted annual rate
    "BABATOTALSASAUS": {
        "label": "Total Business Applications (SA Annual Rate)",
        "type": "ba",
        "frequency": "monthly",
        "seasonal_adj": True,
        "description": "Seasonally adjusted annual rate of total business applications.",
    },
    # High-propensity, weekly, NSA
    "HBABATOTALSAUS": {
        "label": "High-Propensity Business Applications (Weekly, NSA)",
        "type": "hba",
        "frequency": "weekly",
        "seasonal_adj": False,
        "description": (
            "Business applications with a high propensity of becoming "
            "an employer business, United States."
        ),
    },
    # High-propensity, 4-week MA, NSA
    "HBABATOTALMAVG4SAUS": {
        "label": "High-Propensity Business Applications – 4-Week Moving Avg (NSA)",
        "type": "hba",
        "frequency": "weekly",
        "seasonal_adj": False,
        "description": "4-week moving average of high-propensity business applications.",
    },
    # High-propensity, seasonally adjusted annual rate
    "HBABATOTALSASAUS": {
        "label": "High-Propensity Business Applications (SA Annual Rate)",
        "type": "hba",
        "frequency": "monthly",
        "seasonal_adj": True,
        "description": (
            "Seasonally adjusted annual rate of high-propensity "
            "business applications, United States."
        ),
    },
}

# ---------------------------------------------------------------------------
# Industry-level series (quarterly, not seasonally adjusted unless noted)
# Industry series IDs encode the 2-digit NAICS code.
# Census/FRED uses the pattern:
#   BABA<NAICS>NQNSA  – Business Applications, <NAICS>, Not Quarterly (monthly?), NSA
# The most consistently available set uses quarterly frequency.
# ---------------------------------------------------------------------------

# Each entry: naics_code -> {label, ba_id, hba_id, naics_desc}
_INDUSTRY_RAW: list[dict] = [
    {
        "naics": "11",
        "label": "Agriculture, Forestry, Fishing & Hunting",
        "ba_id": "BABA11NQNSA",
        "hba_id": "HBABA11NQNSA",
    },
    {
        "naics": "21",
        "label": "Mining, Quarrying & Oil and Gas Extraction",
        "ba_id": "BABA21NQNSA",
        "hba_id": "HBABA21NQNSA",
    },
    {
        "naics": "22",
        "label": "Utilities",
        "ba_id": "BABA22NQNSA",
        "hba_id": "HBABA22NQNSA",
    },
    {
        "naics": "23",
        "label": "Construction",
        "ba_id": "BABA23NQNSA",
        "hba_id": "HBABA23NQNSA",
    },
    {
        "naics": "31",
        "label": "Manufacturing",
        "ba_id": "BABA31NQNSA",
        "hba_id": "HBABA31NQNSA",
    },
    {
        "naics": "42",
        "label": "Wholesale Trade",
        "ba_id": "BABA42NQNSA",
        "hba_id": "HBABA42NQNSA",
    },
    {
        "naics": "44",
        "label": "Retail Trade",
        "ba_id": "BABA44NQNSA",
        "hba_id": "HBABA44NQNSA",
    },
    {
        "naics": "48",
        "label": "Transportation & Warehousing",
        "ba_id": "BABA48NQNSA",
        "hba_id": "HBABA48NQNSA",
    },
    {
        "naics": "51",
        "label": "Information",
        "ba_id": "BABA51NQNSA",
        "hba_id": "HBABA51NQNSA",
    },
    {
        "naics": "52",
        "label": "Finance & Insurance",
        "ba_id": "BABA52NQNSA",
        "hba_id": "HBABA52NQNSA",
    },
    {
        "naics": "53",
        "label": "Real Estate & Rental and Leasing",
        "ba_id": "BABA53NQNSA",
        "hba_id": "HBABA53NQNSA",
    },
    {
        "naics": "54",
        "label": "Professional, Scientific & Technical Services",
        "ba_id": "BABA54NQNSA",
        "hba_id": "HBABA54NQNSA",
    },
    {
        "naics": "55",
        "label": "Management of Companies & Enterprises",
        "ba_id": "BABA55NQNSA",
        "hba_id": "HBABA55NQNSA",
    },
    {
        "naics": "56",
        "label": "Administrative & Support / Waste Management",
        "ba_id": "BABA56NQNSA",
        "hba_id": "HBABA56NQNSA",
    },
    {
        "naics": "61",
        "label": "Educational Services",
        "ba_id": "BABA61NQNSA",
        "hba_id": "HBABA61NQNSA",
    },
    {
        "naics": "62",
        "label": "Health Care & Social Assistance",
        "ba_id": "BABA62NQNSA",
        "hba_id": "HBABA62NQNSA",
    },
    {
        "naics": "71",
        "label": "Arts, Entertainment & Recreation",
        "ba_id": "BABA71NQNSA",
        "hba_id": "HBABA71NQNSA",
    },
    {
        "naics": "72",
        "label": "Accommodation & Food Services",
        "ba_id": "BABA72NQNSA",
        "hba_id": "HBABA72NQNSA",
    },
    {
        "naics": "81",
        "label": "Other Services (excl. Public Administration)",
        "ba_id": "BABA81NQNSA",
        "hba_id": "HBABA81NQNSA",
    },
    {
        "naics": "99",
        "label": "Unclassified",
        "ba_id": "BABA99NQNSA",
        "hba_id": "HBABA99NQNSA",
    },
]

# Build the public INDUSTRY_SERIES dict keyed by human-readable label
INDUSTRY_SERIES: dict[str, dict] = {
    entry["label"]: {
        "naics": entry["naics"],
        "ba_id": entry["ba_id"],
        "hba_id": entry["hba_id"],
    }
    for entry in _INDUSTRY_RAW
}

# Flat list of every series ID we know about
SERIES_CATALOG: dict[str, dict] = {**TOTAL_SERIES}
for entry in _INDUSTRY_RAW:
    SERIES_CATALOG[entry["ba_id"]] = {
        "label": f"Business Applications – {entry['label']} (NSA)",
        "type": "ba",
        "frequency": "quarterly",
        "seasonal_adj": False,
        "naics": entry["naics"],
    }
    SERIES_CATALOG[entry["hba_id"]] = {
        "label": f"High-Propensity Business Applications – {entry['label']} (NSA)",
        "type": "hba",
        "frequency": "quarterly",
        "seasonal_adj": False,
        "naics": entry["naics"],
    }

ALL_SERIES_IDS: list[str] = list(SERIES_CATALOG.keys())

# Convenience: just the industry names in sorted order
INDUSTRY_NAMES: list[str] = sorted(INDUSTRY_SERIES.keys())
