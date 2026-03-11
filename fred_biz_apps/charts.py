"""
Reusable Plotly chart helpers for BFS data.

All functions return a plotly.graph_objects.Figure that can be embedded
directly in Shiny or exported to HTML / PNG.
"""

from __future__ import annotations

from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# A colour-blind-friendly discrete palette (12 colours)
_PALETTE = px.colors.qualitative.Safe


_SOURCE_NOTE = (
    "Source: U.S. Census Bureau, Business Formation Statistics, "
    "retrieved from FRED, Federal Reserve Bank of St. Louis"
)


def _ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    return df


def _infer_ma_window(df: pd.DataFrame) -> int:
    """Return a ~3-month rolling window appropriate for the data's frequency."""
    if len(df) < 3:
        return 3
    gaps = df.index.to_series().diff().dropna()
    median_days = gaps.median().days
    if median_days <= 10:
        return 13   # weekly  → 13 weeks ≈ 3 months
    elif median_days <= 35:
        return 3    # monthly → 3 months
    else:
        return 1    # quarterly → 1 quarter (= 3 months; shown but minimal smoothing)


def _add_source_annotation(fig: go.Figure) -> None:
    """Append the standard FRED/Census source note to a figure."""
    fig.add_annotation(
        text=_SOURCE_NOTE,
        xref="paper", yref="paper",
        x=0, y=-0.12,
        showarrow=False,
        font=dict(size=10, color="gray"),
        align="left",
        xanchor="left",
    )


def time_series_chart(
    df: pd.DataFrame,
    columns: Iterable[str] | None = None,
    title: str = "Business Applications Over Time",
    y_label: str = "Applications",
    start: str | None = None,
    end: str | None = None,
    mode: str = "lines",
    show_range_selector: bool = True,
    show_ma: bool = False,
) -> go.Figure:
    """
    Multi-line time series chart.

    Parameters
    ----------
    df : DataFrame
        Wide DataFrame indexed by date; columns = series names.
    columns : list of str, optional
        Subset of columns to plot.  Defaults to all columns.
    title : str
        Chart title.
    y_label : str
        Y-axis label.
    start, end : str, optional
        Restrict the x-axis to this date range (YYYY-MM-DD).
    mode : str
        Plotly trace mode – "lines", "lines+markers", "markers".
    show_range_selector : bool
        Add a time-range selector / slider to the x-axis.
    show_ma : bool
        Overlay a 3-month moving average as a dashed line in the same colour.
    """
    df = _ensure_datetime_index(df)

    if start:
        df = df[df.index >= start]
    if end:
        df = df[df.index <= end]

    cols = list(columns) if columns is not None else list(df.columns)
    cols = [c for c in cols if c in df.columns]

    ma_window = _infer_ma_window(df) if show_ma else 1

    fig = go.Figure()
    for i, col in enumerate(cols):
        colour = _PALETTE[i % len(_PALETTE)]
        series = df[col].dropna()

        # Level trace
        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                name=col,
                legendgroup=col,
                mode=mode,
                line=dict(color=colour, width=2),
                hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.0f}<extra>" + col + "</extra>",
            )
        )

        # 3-month MA trace (same colour, dashed)
        if show_ma and ma_window > 1:
            ma = series.rolling(window=ma_window, min_periods=1).mean()
            fig.add_trace(
                go.Scatter(
                    x=ma.index,
                    y=ma.values,
                    name=f"{col} (3M MA)",
                    legendgroup=col,
                    showlegend=True,
                    mode="lines",
                    line=dict(color=colour, width=1.5, dash="dash"),
                    hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.0f}<extra>" + col + " (3M MA)</extra>",
                )
            )

    xaxis_cfg: dict = dict(title="Date")
    if show_range_selector:
        xaxis_cfg["rangeselector"] = dict(
            buttons=[
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=3, label="3Y", step="year", stepmode="backward"),
                dict(count=5, label="5Y", step="year", stepmode="backward"),
                dict(count=10, label="10Y", step="year", stepmode="backward"),
                dict(step="all", label="All"),
            ]
        )
        xaxis_cfg["rangeslider"] = dict(visible=False)

    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis=xaxis_cfg,
        yaxis=dict(title=y_label, tickformat=",d"),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
        ),
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=60, r=180, t=60, b=80),
    )
    _add_source_annotation(fig)
    return fig


def bar_chart_latest(
    df: pd.DataFrame,
    title: str = "Latest Business Applications by Industry",
    y_label: str = "Applications",
    n_periods: int = 4,
) -> go.Figure:
    """
    Horizontal bar chart of the most recent n_periods average for each column.
    Useful to compare industries at-a-glance.
    """
    df = _ensure_datetime_index(df).sort_index()
    recent = df.tail(n_periods).mean().sort_values(ascending=True)

    colours = [_PALETTE[i % len(_PALETTE)] for i in range(len(recent))]

    fig = go.Figure(
        go.Bar(
            y=recent.index.tolist(),
            x=recent.values,
            orientation="h",
            marker=dict(color=colours),
            hovertemplate="%{y}<br>%{x:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis=dict(title=y_label, tickformat=",d"),
        yaxis=dict(title=""),
        template="plotly_white",
        margin=dict(l=220, r=40, t=60, b=60),
        height=max(400, 30 * len(recent) + 120),
    )
    return fig


def indexed_chart(
    df: pd.DataFrame,
    columns: Iterable[str] | None = None,
    title: str = "Indexed Business Applications",
    start: str | None = None,
    end: str | None = None,
    base_date: str | None = None,
    show_range_selector: bool = True,
) -> go.Figure:
    """
    Index chart: all series normalized to 100 at *base_date*.

    Parameters
    ----------
    base_date : str, optional
        YYYY-MM-DD string for the reference period.  The nearest available
        observation date is used when an exact match is not found.
        Defaults to the first observation in the data.
    """
    df = _ensure_datetime_index(df).sort_index()

    cols = list(columns) if columns is not None else list(df.columns)
    cols = [c for c in cols if c in df.columns]

    base_dt = pd.to_datetime(base_date) if base_date else df.index[0]
    base_label = base_dt.strftime("%B %Y")

    fig = go.Figure()
    for i, col in enumerate(cols):
        colour = _PALETTE[i % len(_PALETTE)]
        series = df[col].dropna()

        # Find the observation whose year-month matches the chosen base period
        mask = (series.index.year == base_dt.year) & (series.index.month == base_dt.month)
        if not mask.any():
            continue
        base_val = series[mask].iloc[0]
        if pd.isna(base_val) or base_val == 0:
            continue

        indexed = (series / base_val) * 100

        if start:
            indexed = indexed[indexed.index >= start]
        if end:
            indexed = indexed[indexed.index <= end]

        fig.add_trace(
            go.Scatter(
                x=indexed.index,
                y=indexed.values,
                name=col,
                mode="lines",
                line=dict(color=colour, width=2),
                hovertemplate="%{x|%Y-%m-%d}<br>%{y:.1f}<extra>" + col + "</extra>",
            )
        )

    # Reference line at 100
    fig.add_hline(y=100, line_dash="dash", line_color="gray", line_width=1)

    xaxis_cfg: dict = dict(title="Date")
    if show_range_selector:
        xaxis_cfg["rangeselector"] = dict(
            buttons=[
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=3, label="3Y", step="year", stepmode="backward"),
                dict(count=5, label="5Y", step="year", stepmode="backward"),
                dict(count=10, label="10Y", step="year", stepmode="backward"),
                dict(step="all", label="All"),
            ]
        )
        xaxis_cfg["rangeslider"] = dict(visible=False)

    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis=xaxis_cfg,
        yaxis=dict(title=f"Index ({base_label} = 100)"),
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.01),
        margin=dict(l=60, r=180, t=60, b=100),
    )

    # Explanatory note – updates dynamically with the chosen base period
    fig.add_annotation(
        text=f"Index: {base_label} = 100",
        xref="paper", yref="paper",
        x=0, y=-0.10,
        showarrow=False,
        font=dict(size=11, color="dimgray"),
        align="left",
        xanchor="left",
    )
    fig.add_annotation(
        text=_SOURCE_NOTE,
        xref="paper", yref="paper",
        x=0, y=-0.16,
        showarrow=False,
        font=dict(size=10, color="gray"),
        align="left",
        xanchor="left",
    )
    return fig


def yoy_change_chart(
    df: pd.DataFrame,
    columns: Iterable[str] | None = None,
    title: str = "Year-over-Year % Change",
    start: str | None = None,
    end: str | None = None,
) -> go.Figure:
    """
    Year-over-year percentage change for selected columns.
    Works for both weekly (52-period shift) and quarterly (4-period shift) data
    by inferring the dominant frequency.
    """
    df = _ensure_datetime_index(df).sort_index()

    # Infer shift based on median gap between observations
    if len(df) > 2:
        gaps = df.index.to_series().diff().dropna()
        median_days = gaps.median().days
        if median_days <= 10:
            shift = 52  # weekly
        elif median_days <= 35:
            shift = 12  # monthly
        else:
            shift = 4   # quarterly
    else:
        shift = 4

    cols = list(columns) if columns is not None else list(df.columns)
    cols = [c for c in cols if c in df.columns]

    yoy = df[cols].pct_change(periods=shift) * 100

    if start:
        yoy = yoy[yoy.index >= start]
    if end:
        yoy = yoy[yoy.index <= end]

    fig = go.Figure()
    for i, col in enumerate(cols):
        colour = _PALETTE[i % len(_PALETTE)]
        s = yoy[col].dropna()
        fig.add_trace(
            go.Scatter(
                x=s.index,
                y=s.values,
                name=col,
                mode="lines",
                line=dict(color=colour, width=2),
                hovertemplate="%{x|%Y-%m-%d}<br>%{y:.1f}%<extra>" + col + "</extra>",
            )
        )

    # Zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)

    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis=dict(title="Date"),
        yaxis=dict(title="YoY Change (%)"),
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.01),
        margin=dict(l=60, r=180, t=60, b=80),
    )
    _add_source_annotation(fig)
    return fig
