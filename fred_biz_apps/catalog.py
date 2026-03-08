"""
Catalog of FRED Business Formation Statistics (BFS) series.

Series-ID naming convention used by FRED/Census:
    BABA   = Business Applications
    BAHBA  = High-Propensity Business Applications
    NAICS  = North American Industry Classification System sector
    SA/NSA = Seasonally Adjusted / Not Seasonally Adjusted
    AUS    = United States

Monthly aggregate series examples (confirmed on FRED):
    BABATOTALSAUS   – Total BA, Monthly SA
    BABATOTALNSAUS  – Total BA, Monthly NSA
    BAHBATOTALSAUS  – Total HBA, Monthly SA
    BAHBATOTALNSAUS – Total HBA, Monthly NSA

Industry series follow: BABANAICS{code_or_abbrev}{SA|NS}AUS
  e.g. BABANAICS52SAUS, BABANAICSMNFNSAUS, BABANAICSRETNSAUS
HBA industry series: BAHBANAICS{code_or_abbrev}{SA|NS}AUS
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Aggregate / "Total" series  (monthly, national)
# ---------------------------------------------------------------------------

TOTAL_SERIES: dict[str, dict] = {
    # Monthly, seasonally adjusted
    "BABATOTALSAUS": {
        "label": "Total Business Applications (SA)",
        "type": "ba",
        "frequency": "monthly",
        "seasonal_adj": True,
        "description": "Total business applications filed with the IRS, United States, seasonally adjusted.",
    },
    # Monthly, not seasonally adjusted
    "BABATOTALNSAUS": {
        "label": "Total Business Applications (NSA)",
        "type": "ba",
        "frequency": "monthly",
        "seasonal_adj": False,
        "description": "Total business applications filed with the IRS, United States, not seasonally adjusted.",
    },
    # High-propensity, monthly, SA
    "BAHBATOTALSAUS": {
        "label": "High-Propensity Business Applications (SA)",
        "type": "hba",
        "frequency": "monthly",
        "seasonal_adj": True,
        "description": (
            "Business applications with a high propensity of becoming "
            "an employer business, United States, seasonally adjusted."
        ),
    },
    # High-propensity, monthly, NSA
    "BAHBATOTALNSAUS": {
        "label": "High-Propensity Business Applications (NSA)",
        "type": "hba",
        "frequency": "monthly",
        "seasonal_adj": False,
        "description": (
            "Business applications with a high propensity of becoming "
            "an employer business, United States, not seasonally adjusted."
        ),
    },
}

# ---------------------------------------------------------------------------
# Industry-level series (monthly, national)
#
# BA  series pattern : BABANAICS{code}SAUS  or BABANAICS{abbrev}NSAUS
# HBA series pattern : BAHBANAICS{code}SAUS or BAHBANAICS{abbrev}NSAUS
#
# Multi-code NAICS sectors use text abbreviations on FRED:
#   Manufacturing (31-33) → MNF
#   Retail Trade  (44-45) → RET
#   Transportation (48-49) → TRAN  (inferred from naming pattern)
# ---------------------------------------------------------------------------

_INDUSTRY_RAW: list[dict] = [
    {
        "naics": "11",
        "label": "Agriculture, Forestry, Fishing & Hunting",
        "ba_id":  "BABANAICS11NSAUS",
        "hba_id": "BAHBANAICS11NSAUS",
    },
    {
        "naics": "21",
        "label": "Mining, Quarrying & Oil and Gas Extraction",
        "ba_id":  "BABANAICS21SAUS",
        "hba_id": "BAHBANAICS21SAUS",
    },
    {
        "naics": "22",
        "label": "Utilities",
        "ba_id":  "BABANAICS22NSAUS",
        "hba_id": "BAHBANAICS22NSAUS",
    },
    {
        "naics": "23",
        "label": "Construction",
        "ba_id":  "BABANAICS23SAUS",
        "hba_id": "BAHBANAICS23SAUS",
    },
    {
        "naics": "3133",
        "label": "Manufacturing",
        "ba_id":  "BABANAICSMNFNSAUS",
        "hba_id": "BAHBANAICSMNFNSAUS",
    },
    {
        "naics": "42",
        "label": "Wholesale Trade",
        "ba_id":  "BABANAICS42SAUS",
        "hba_id": "BAHBANAICS42SAUS",
    },
    {
        "naics": "4445",
        "label": "Retail Trade",
        "ba_id":  "BABANAICSRETNSAUS",
        "hba_id": "BAHBANAICSRETNSAUS",
    },
    {
        "naics": "4849",
        "label": "Transportation & Warehousing",
        "ba_id":  "BABANAICSTWSAUS",
        "hba_id": "BAHBANAICSTWNSAUS",
    },
    {
        "naics": "51",
        "label": "Information",
        "ba_id":  "BABANAICS51SAUS",
        "hba_id": "BAHBANAICS51SAUS",
    },
    {
        "naics": "52",
        "label": "Finance & Insurance",
        "ba_id":  "BABANAICS52SAUS",
        "hba_id": "BAHBANAICS52SAUS",
    },
    {
        "naics": "53",
        "label": "Real Estate & Rental and Leasing",
        "ba_id":  "BABANAICS53SAUS",
        "hba_id": "BAHBANAICS53SAUS",
    },
    {
        "naics": "54",
        "label": "Professional, Scientific & Technical Services",
        "ba_id":  "BABANAICS54SAUS",
        "hba_id": "BAHBANAICS54SAUS",
    },
    {
        "naics": "55",
        "label": "Management of Companies & Enterprises",
        "ba_id":  "BABANAICS55SAUS",
        "hba_id": "BAHBANAICS55NSAUS",
    },
    {
        "naics": "56",
        "label": "Administrative & Support / Waste Management",
        "ba_id":  "BABANAICS56SAUS",
        "hba_id": "BAHBANAICS56SAUS",
    },
    {
        "naics": "61",
        "label": "Educational Services",
        "ba_id":  "BABANAICS61SAUS",
        "hba_id": "BAHBANAICS61SAUS",
    },
    {
        "naics": "62",
        "label": "Health Care & Social Assistance",
        "ba_id":  "BABANAICS62SAUS",
        "hba_id": "BAHBANAICS62SAUS",
    },
    {
        "naics": "71",
        "label": "Arts, Entertainment & Recreation",
        "ba_id":  "BABANAICS71SAUS",
        "hba_id": "BAHBANAICS71NSAUS",
    },
    {
        "naics": "72",
        "label": "Accommodation & Food Services",
        "ba_id":  "BABANAICS72SAUS",
        "hba_id": "BAHBANAICS72NSAUS",
    },
    {
        "naics": "81",
        "label": "Other Services (excl. Public Administration)",
        "ba_id":  "BABANAICS81SAUS",
        "hba_id": "BAHBANAICS81SAUS",
    },
]

# Build the public INDUSTRY_SERIES dict keyed by human-readable label
INDUSTRY_SERIES: dict[str, dict] = {
    entry["label"]: {
        "naics":  entry["naics"],
        "ba_id":  entry["ba_id"],
        "hba_id": entry["hba_id"],
    }
    for entry in _INDUSTRY_RAW
}

# Flat dict of every series ID we know about
SERIES_CATALOG: dict[str, dict] = {**TOTAL_SERIES}
for entry in _INDUSTRY_RAW:
    SERIES_CATALOG[entry["ba_id"]] = {
        "label": f"Business Applications – {entry['label']}",
        "type": "ba",
        "frequency": "monthly",
        "seasonal_adj": entry["ba_id"].endswith("SAUS"),
        "naics": entry["naics"],
    }
    SERIES_CATALOG[entry["hba_id"]] = {
        "label": f"High-Propensity Business Applications – {entry['label']}",
        "type": "hba",
        "frequency": "monthly",
        "seasonal_adj": entry["hba_id"].endswith("SAUS"),
        "naics": entry["naics"],
    }

ALL_SERIES_IDS: list[str] = list(SERIES_CATALOG.keys())

# Convenience: just the industry names in sorted order
INDUSTRY_NAMES: list[str] = sorted(INDUSTRY_SERIES.keys())
