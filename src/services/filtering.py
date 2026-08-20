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


def apply_time_window(df: pd.DataFrame, hours_back: int, now: datetime | None = None) -> pd.DataFrame:
    """Slice an in-memory dataframe to the given lookback window.

    Only needed for the demo data source; Oracle queries already scope the
    time window in SQL.
    """
    now = now or datetime.now()
    cutoff = now - timedelta(hours=hours_back)
    return df[df["START_TIME"] >= cutoff]


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
