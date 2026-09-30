"""Orchestrates which data source (Oracle vs. demo) backs the dashboard.

Streamlit's ``st.cache_data`` is applied here, at the boundary between the
UI and the data layer, so the repository/service modules underneath stay
free of Streamlit-specific concerns and are easy to unit test.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config.settings import AppSettings, OracleSettings
from src.database.repositories.process_run_repository import fetch_process_runs, fetch_task_catalog
from src.services.demo_data_service import generate_demo_data_with_settings
from src.services.filtering import apply_time_window, window_start
from src.services import metrics_service

DataSource = str  # "Oracle DB" | "Demo data"

ORACLE_SOURCE: DataSource = "Oracle DB"
DEMO_SOURCE: DataSource = "Demo data"


# Keyed on the window *label* (not a datetime) so rolling windows still hit the
# cache. TTL is kept below the auto-refresh interval so refreshes see new rows.
@st.cache_data(ttl=20)
def _cached_fetch_process_runs(
    oracle_settings: OracleSettings,
    app_settings: AppSettings,
    window: str,
) -> tuple[pd.DataFrame, str | None]:
    return fetch_process_runs(oracle_settings, app_settings, since=window_start(window))


@st.cache_data(ttl=300)
def _cached_fetch_task_catalog(oracle_settings: OracleSettings, app_settings: AppSettings) -> pd.DataFrame:
    df, _ = fetch_task_catalog(oracle_settings, app_settings)
    return df


def load_data(
    source: DataSource,
    oracle_settings: OracleSettings,
    app_settings: AppSettings,
    window: str,
) -> tuple[pd.DataFrame, str | None]:
    """Load process-run data from the requested source for a preset window.

    Returns (dataframe, error). ``error`` is only ever set for the Oracle
    source; demo data generation cannot fail.
    """
    if source == ORACLE_SOURCE:
        return _cached_fetch_process_runs(oracle_settings, app_settings, window)
    demo = generate_demo_data_with_settings(app_settings)
    return apply_time_window(demo, window), None


def load_task_catalog(source: DataSource, oracle_settings: OracleSettings, app_settings: AppSettings) -> pd.DataFrame:
    """All-time (process, task) catalog, independent of the selected window."""
    if source == ORACLE_SOURCE:
        return _cached_fetch_task_catalog(oracle_settings, app_settings)
    return metrics_service.catalog_from_runs(generate_demo_data_with_settings(app_settings))
