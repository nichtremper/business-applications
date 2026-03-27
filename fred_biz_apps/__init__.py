"""
fred-biz-apps
=============
Download, cache, and visualize FRED Business Formation Statistics (BFS) data.

Quick start
-----------
>>> from fred_biz_apps import BFSDownloader
>>> dl = BFSDownloader(api_key="YOUR_FRED_API_KEY")
>>> df = dl.get_all()          # all series, returns a wide DataFrame
>>> df_industry = dl.get_by_industry()
"""

from .client import FREDClient
from .catalog import SERIES_CATALOG, INDUSTRY_SERIES, ALL_SERIES_IDS, NORMALIZABLE_INDUSTRIES
from .downloader import BFSDownloader

__all__ = [
    "FREDClient",
    "SERIES_CATALOG",
    "INDUSTRY_SERIES",
    "ALL_SERIES_IDS",
    "NORMALIZABLE_INDUSTRIES",
    "BFSDownloader",
]
