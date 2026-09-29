"""Applies sidebar filter selections to a process-run dataframe.

Pure functions (no Streamlit imports) so they can be unit tested directly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

import pandas as pd


@dataclass(frozen=True)
class RunFilters:
    process_types: list[str] = field(default_factory=list)
    process_names: list[str] = field(default_factory=list)
    task_names: list[str] = field(default_factory=list)
    statuses: list[str] = field(default_factory=list)


def apply_filters(df: pd.DataFrame, filters: RunFilters) -> pd.DataFrame:
    """Apply the sidebar multiselect filters. Empty lists mean 'no filter'."""
    if filters.process_types:
        df = df[df["PROCESS_TYPE"].isin(filters.process_types)]
    if filters.process_names:
        df = df[df["PROCESS_NAME"].isin(filters.process_names)]
    if filters.task_names:
        df = df[df["TASK_NAME"].isin(filters.task_names)]
    if filters.statuses:
        df = df[df["STATUS_NAME"].isin(filters.statuses)]
    return df


def window_start(window: str, now: datetime | None = None) -> datetime | None:
    """Start of the preset window; None means unbounded (All time)."""
    now = now or datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return {
        "Today": midnight,
        "Yesterday + today": midnight - timedelta(days=1),
        "1 week": now - timedelta(days=7),
        "1 month": now - timedelta(days=30),
        "All time": None,
    }[window]


def apply_time_window(df: pd.DataFrame, window: str, now: datetime | None = None) -> pd.DataFrame:
    """Slice an in-memory dataframe to the given preset window.

    Only needed for the demo data source; Oracle queries already scope the
    time window in SQL.
    """
    start = window_start(window, now)
    return df if start is None else df[df["START_TIME"] >= start]


def apply_search(df: pd.DataFrame, search_text: str) -> pd.DataFrame:
    """Case-insensitive substring search across process name, table, run id."""
    if not search_text:
        return df
    mask = (
        df["PROCESS_NAME"].str.contains(search_text, case=False, na=False)
        | df["TARGET_TABLE"].str.contains(search_text, case=False, na=False)
        | df["PROCESS_RUN_ID"].str.contains(search_text, case=False, na=False)
    )
    return df[mask]
