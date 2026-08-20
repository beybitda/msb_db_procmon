"""Orchestrates which data source (Oracle vs. demo) backs the dashboard.

Streamlit's ``st.cache_data`` is applied here, at the boundary between the
UI and the data layer, so the repository/service modules underneath stay
free of Streamlit-specific concerns and are easy to unit test.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config.settings import AppSettings, OracleSettings
from src.database.repositories.process_run_repository import fetch_process_runs
from src.services.demo_data_service import generate_demo_data_with_settings

DataSource = str  # "Oracle DB" | "Demo data"

ORACLE_SOURCE: DataSource = "Oracle DB"
DEMO_SOURCE: DataSource = "Demo data"


@st.cache_data(ttl=30)
def _cached_fetch_process_runs(
    oracle_settings: OracleSettings,
    app_settings: AppSettings,
    hours_back: int,
) -> tuple[pd.DataFrame, str | None]:
    return fetch_process_runs(oracle_settings, app_settings, hours_back=hours_back)


def load_data(
    source: DataSource,
    oracle_settings: OracleSettings,
    app_settings: AppSettings,
    hours_back: int,
) -> tuple[pd.DataFrame, str | None]:
    """Load process-run data from the requested source.

    Returns (dataframe, error). ``error`` is only ever set for the Oracle
    source; demo data generation cannot fail.
    """
    if source == ORACLE_SOURCE:
        return _cached_fetch_process_runs(oracle_settings, app_settings, hours_back)
    return generate_demo_data_with_settings(app_settings), None
