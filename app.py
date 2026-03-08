"""
FRED Business Formation Statistics – Shiny for Python App
==========================================================

Run locally:
    shiny run app.py

Environment variable (alternative to typing key in the UI):
    FRED_API_KEY=your_key_here shiny run app.py
"""

from __future__ import annotations

import os
from datetime import date, datetime
from typing import Optional

import pandas as pd
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.types import NavSetArg

from fred_biz_apps import BFSDownloader
from fred_biz_apps.catalog import INDUSTRY_NAMES
from fred_biz_apps.charts import (
    time_series_chart,
    yoy_change_chart,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_API_KEY = os.environ.get("FRED_API_KEY", "")
_DEFAULT_START = "2006-01-01"
_DEFAULT_END = date.today().isoformat()
_CACHE_DIR = "bfs_cache"

# For aggregate panel the user picks from labelled series groups
_TOTAL_SERIES_CHOICES = {
    "Total Business Applications (SA)": "Total Business Applications (SA)",
    "Total Business Applications (NSA)": "Total Business Applications (NSA)",
    "High-Propensity Business Applications (SA)": "High-Propensity Business Applications (SA)",
    "High-Propensity Business Applications (NSA)": "High-Propensity Business Applications (NSA)",
}

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------


def _sidebar() -> ui.Tag:
    return ui.sidebar(
        ui.h5("Settings"),
        # --- API key ---
        ui.input_text(
            "api_key",
            "FRED API Key",
            value=_DEFAULT_API_KEY,
            placeholder="Enter your FRED API key…",
        ),
        ui.input_action_button("fetch", "Fetch / Refresh Data", class_="btn-primary w-100 mt-1"),
        ui.hr(),
        # --- Date range ---
        ui.h6("Date Range"),
        ui.input_date("start_date", "Start", value=_DEFAULT_START),
        ui.input_date("end_date", "End", value=_DEFAULT_END),
        ui.hr(),
        # --- Chart type ---
        ui.h6("Chart Type"),
        ui.input_radio_buttons(
            "chart_type",
            None,
            choices={"level": "Level", "yoy": "Year-over-Year % Change"},
            selected="level",
        ),
        ui.panel_conditional(
            "input.chart_type === 'level'",
            ui.input_checkbox(
                "show_ma",
                "Overlay 3-month moving average",
                value=False,
            ),
        ),
        ui.hr(),
        # --- Totals filter (shown on Totals tab or Industry tab when "All" selected) ---
        ui.panel_conditional(
            "input.tabs === 'totals' || (input.tabs === 'industry' && input.industry_sel && input.industry_sel.indexOf('All') > -1)",
            ui.h6("Series to Display"),
            ui.input_checkbox_group(
                "total_series_sel",
                None,
                choices=_TOTAL_SERIES_CHOICES,
                selected=list(_TOTAL_SERIES_CHOICES.keys())[:3],
            ),
        ),
        # --- Industry filter (shown only on Industry tab) ---
        ui.panel_conditional(
            "input.tabs === 'industry'",
            ui.h6("Series Type"),
            ui.input_radio_buttons(
                "ind_type",
                None,
                choices={"ba": "Business Applications", "hba": "High-Propensity"},
                selected="ba",
            ),
            ui.h6("Industries"),
            ui.input_selectize(
                "industry_sel",
                None,
                choices=["All"] + INDUSTRY_NAMES,
                selected=["All"],
                multiple=True,
                options={"placeholder": "Type to search…"},
            ),
        ),
        width=320,
        open="desktop",
    )


app_ui = ui.page_navbar(
    ui.nav_panel(
        "Totals",
        ui.value_box(
            "Data Status",
            ui.output_text("status_box"),
            theme="bg-gradient-blue-purple",
        ),
        ui.card(
            ui.card_header("Business Applications Over Time"),
            ui.output_ui("plot_totals"),
            full_screen=True,
        ),
        value="totals",
    ),
    ui.nav_panel(
        "By Industry",
        ui.card(
            ui.card_header("Business Applications by Industry"),
            ui.output_ui("plot_industry"),
            full_screen=True,
        ),
        value="industry",
    ),
    ui.nav_panel(
        "Data Table",
        ui.card(
            ui.card_header(
                ui.div(
                    "Raw Data",
                    ui.download_button(
                        "download_csv",
                        "Download CSV",
                        class_="btn-sm btn-outline-secondary",
                    ),
                    class_="d-flex justify-content-between align-items-center w-100",
                )
            ),
            ui.output_data_frame("data_table"),
        ),
        value="table",
    ),
    ui.nav_spacer(),
    ui.nav_control(
        ui.a(
            "FRED BFS Documentation",
            href="https://www.census.gov/econ/bfs/index.html",
            target="_blank",
            class_="nav-link",
        )
    ),
    id="tabs",
    title="FRED Business Formation Statistics",
    sidebar=_sidebar(),
    fillable=True,
    theme=ui.Theme("bootstrap"),
)

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------


def server(input: Inputs, output: Outputs, session: Session) -> None:

    # Reactive store for downloaded data
    _data: reactive.Value[dict | None] = reactive.value(None)
    _status: reactive.Value[str] = reactive.value("No data loaded. Enter your API key and click Fetch.")

    # ------------------------------------------------------------------
    # Data fetch
    # ------------------------------------------------------------------

    @reactive.effect
    @reactive.event(input.fetch)
    def _fetch():
        key = input.api_key().strip()
        if not key:
            _status.set("Please enter a FRED API key.")
            return

        start = str(input.start_date())
        end = str(input.end_date())

        _status.set("Downloading data from FRED…")
        try:
            dl = BFSDownloader(api_key=key, cache_dir=_CACHE_DIR)
            data = dl.get_all(start=start, end=end)
            _data.set(data)
            sizes = {k: len(v) for k, v in data.items() if isinstance(v, pd.DataFrame)}
            _status.set(
                f"Loaded. Totals: {sizes.get('totals', 0)} obs · "
                f"Industry BA: {sizes.get('industry_ba', 0)} obs · "
                f"Industry HBA: {sizes.get('industry_hba', 0)} obs"
            )
        except Exception as exc:
            _status.set(f"Error: {exc}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _date_range() -> tuple[str, str]:
        return str(input.start_date()), str(input.end_date())

    def _active_industry_df() -> pd.DataFrame:
        data = _data()
        if data is None:
            return pd.DataFrame()

        sel = list(input.industry_sel())
        industry_names = [s for s in sel if s != "All"]
        include_totals = "All" in sel

        frames: list[pd.DataFrame] = []

        if include_totals:
            totals_df = data.get("totals", pd.DataFrame())
            if not totals_df.empty:
                total_sel = list(input.total_series_sel())
                if total_sel:
                    valid_t = [s for s in total_sel if s in totals_df.columns]
                    if valid_t:
                        frames.append(totals_df[valid_t])
                else:
                    frames.append(totals_df)

        if industry_names:
            key = "industry_hba" if input.ind_type() == "hba" else "industry_ba"
            ind_df = data.get(key, pd.DataFrame())
            if not ind_df.empty:
                valid_i = [s for s in industry_names if s in ind_df.columns]
                if valid_i:
                    frames.append(ind_df[valid_i])

        if not frames:
            return pd.DataFrame()
        return frames[0] if len(frames) == 1 else pd.concat(frames, axis=1)

    # ------------------------------------------------------------------
    # Outputs – status
    # ------------------------------------------------------------------

    @render.text
    def status_box() -> str:
        return _status()

    # ------------------------------------------------------------------
    # Outputs – Totals tab
    # ------------------------------------------------------------------

    @render.ui
    def plot_totals():
        data = _data()
        if data is None or data["totals"].empty:
            return ui.p("No data. Click 'Fetch / Refresh Data'.", class_="text-muted p-3")

        df = data["totals"]
        start, end = _date_range()
        sel = list(input.total_series_sel())
        if not sel:
            sel = list(df.columns)

        if input.chart_type() == "yoy":
            fig = yoy_change_chart(df, columns=sel, start=start, end=end,
                                   title="Business Applications – YoY % Change")
        else:
            fig = time_series_chart(df, columns=sel, start=start, end=end,
                                    title="Business Applications Over Time",
                                    show_ma=bool(input.show_ma()))

        return ui.HTML(fig.to_html(full_html=False, include_plotlyjs="cdn"))

    # ------------------------------------------------------------------
    # Outputs – Industry tab
    # ------------------------------------------------------------------

    @render.ui
    def plot_industry():
        df = _active_industry_df()
        if df.empty:
            return ui.p("No data. Click 'Fetch / Refresh Data'.", class_="text-muted p-3")

        start, end = _date_range()
        series_type_label = (
            "High-Propensity Business Applications"
            if input.ind_type() == "hba"
            else "Business Applications"
        )

        if input.chart_type() == "yoy":
            fig = yoy_change_chart(df, start=start, end=end,
                                   title=f"{series_type_label} by Industry – YoY % Change")
        else:
            fig = time_series_chart(df, start=start, end=end,
                                    title=f"{series_type_label} by Industry",
                                    show_ma=bool(input.show_ma()))

        return ui.HTML(fig.to_html(full_html=False, include_plotlyjs="cdn"))

    # ------------------------------------------------------------------
    # Outputs – Data Table tab
    # ------------------------------------------------------------------

    @render.data_frame
    def data_table():
        data = _data()
        if data is None:
            return render.DataGrid(pd.DataFrame({"info": ["No data loaded."]}))

        active_tab = input.tabs()

        if active_tab == "totals":
            df = data.get("totals", pd.DataFrame())
        else:
            df = _active_industry_df()

        if df.empty:
            return render.DataGrid(pd.DataFrame({"info": ["No data."]}))

        start, end = _date_range()
        df = df.copy()
        df.index = pd.to_datetime(df.index)
        if start:
            df = df[df.index >= start]
        if end:
            df = df[df.index <= end]

        display = df.reset_index().rename(columns={"date": "Date"})
        display["Date"] = display["Date"].dt.strftime("%Y-%m-%d")
        for col in display.columns[1:]:
            display[col] = display[col].map(lambda x: f"{x:,.0f}" if pd.notna(x) else "")

        return render.DataGrid(display, filters=True, height="500px")

    @render.download(filename=lambda: f"bfs_data_{date.today().isoformat()}.csv")
    def download_csv():
        data = _data()
        if data is None:
            yield ""
            return

        active_tab = input.tabs()
        if active_tab == "totals":
            df = data.get("totals", pd.DataFrame()).copy()
            sel = list(input.total_series_sel())
            if sel:
                valid = [s for s in sel if s in df.columns]
                if valid:
                    df = df[valid]
        else:
            df = _active_industry_df().copy()

        start, end = _date_range()
        df.index = pd.to_datetime(df.index)
        if start:
            df = df[df.index >= start]
        if end:
            df = df[df.index <= end]

        yield df.reset_index().rename(columns={"date": "Date"}).to_csv(index=False)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = App(app_ui, server)
