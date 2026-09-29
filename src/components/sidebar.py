"""Sidebar: connection status, time window, filters, and refresh controls.

The sidebar needs a dataframe to populate its multiselect *options* (e.g.
the list of process names), so it necessarily triggers the initial data
load. That load is delegated to ``data_service`` so this module contains
no Oracle/demo-specific logic itself.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from src.config.constants import DEFAULT_TIME_WINDOW, STATUS_NAMES, TIME_WINDOW_OPTIONS
from src.config.settings import AppSettings, OracleSettings
from src.services.data_service import DEMO_SOURCE, ORACLE_SOURCE, load_data
from src.services.filtering import RunFilters


@dataclass(frozen=True)
class SidebarResult:
    source: str
    df_all: pd.DataFrame
    filters: RunFilters
    window: str
    auto_refresh: bool


def _render_connection_status(oracle_settings: OracleSettings) -> str:
    """Renders the connection indicator and returns the selected source."""
    st.markdown("**CONNECTION**")
    if oracle_settings.is_configured:
        st.markdown(
            f'<div style="color:#00D4A0;font-family:\'IBM Plex Mono\',monospace;font-size:10px;">'
            f'⬤ ENV  {oracle_settings.display_target}</div>',
            unsafe_allow_html=True,
        )
        return st.radio("Data source", [ORACLE_SOURCE, DEMO_SOURCE], label_visibility="collapsed")

    st.markdown(
        '<div style="color:#4A5068;font-family:\'IBM Plex Mono\',monospace;font-size:10px;">'
        '○ ENV not set — using demo data</div>',
        unsafe_allow_html=True,
    )
    return DEMO_SOURCE


def render_sidebar(oracle_settings: OracleSettings, app_settings: AppSettings) -> SidebarResult:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">⬡ PROC·MON</div>', unsafe_allow_html=True)

        source = _render_connection_status(oracle_settings)

        st.divider()
        st.markdown("**TIME WINDOW**")
        window = st.radio(
            "Time window",
            TIME_WINDOW_OPTIONS,
            index=TIME_WINDOW_OPTIONS.index(DEFAULT_TIME_WINDOW),
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown("**FILTERS**")

        # Load for the selected window; also populates the filter dropdown options.
        if source == ORACLE_SOURCE:
            with st.spinner("Connecting…"):
                df_all, oracle_error = load_data(ORACLE_SOURCE, oracle_settings, app_settings, window=window)
            if oracle_error or df_all.empty:
                st.error(f"Oracle error — falling back to demo data\n{oracle_error or 'empty result'}")
                source = DEMO_SOURCE
                df_all, _ = load_data(DEMO_SOURCE, oracle_settings, app_settings, window=window)
        else:
            df_all, _ = load_data(DEMO_SOURCE, oracle_settings, app_settings, window=window)

        process_types = st.multiselect(
            "Process type", options=sorted(df_all["PROCESS_TYPE"].unique()),
            default=[], placeholder="All types",
        )
        process_names = st.multiselect(
            "Process name", options=sorted(df_all["PROCESS_NAME"].unique()),
            default=[], placeholder="All processes",
        )
        task_names = st.multiselect(
            "Task name", options=sorted(df_all["TASK_NAME"].unique()),
            default=[], placeholder="All tasks",
        )
        statuses = st.multiselect(
            "Status", options=STATUS_NAMES, default=[], placeholder="All statuses",
        )

        st.divider()
        auto_refresh = st.toggle("Auto-refresh (30s)", value=False)
        if st.button("↺  Refresh now", width='stretch'):
            st.cache_data.clear()
            st.rerun()

    filters = RunFilters(
        process_types=process_types,
        process_names=process_names,
        task_names=task_names,
        statuses=statuses,
    )
    return SidebarResult(
        source=source,
        df_all=df_all,
        filters=filters,
        window=window,
        auto_refresh=auto_refresh,
    )
