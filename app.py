"""Process Monitor — Streamlit entry point.

This file only wires things together: page config, sidebar, data
filtering, and tab rendering. All business logic lives in ``src/``.
"""
import time

import streamlit as st

from src.components import header, kpi_cards
from src.components.sidebar import render_sidebar
from src.components.styles import inject_custom_css
from src.components.tabs import errors_tab, overview_tab, performance_tab, run_log_tab
from src.config.settings import get_app_settings, get_oracle_settings
from src.services import metrics_service
from src.services.data_service import ORACLE_SOURCE, load_data
from src.services.filtering import apply_filters, apply_time_window

app_settings = get_app_settings()
oracle_settings = get_oracle_settings()

st.set_page_config(
    page_title=app_settings.page_title,
    page_icon=app_settings.page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_custom_css()

sidebar = render_sidebar(oracle_settings, app_settings)

# ─── Load data scoped to the chosen time window ─────────────────────────────
# Oracle queries scope the window in SQL; demo data is sliced in-memory.
if sidebar.source == ORACLE_SOURCE:
    df, error = load_data(ORACLE_SOURCE, oracle_settings, app_settings, sidebar.hours_back)
    if error or df.empty:
        df = sidebar.df_all.copy()  # graceful fallback to the pre-loaded frame
else:
    df = apply_time_window(sidebar.df_all.copy(), sidebar.hours_back)

df = apply_filters(df, sidebar.filters)

# ─── Auto-refresh ────────────────────────────────────────────────────────────
if sidebar.auto_refresh:
    time.sleep(app_settings.auto_refresh_seconds)
    st.rerun()

# ─── Header + KPIs ───────────────────────────────────────────────────────────
header.render_header()
kpi_cards.render_kpi_cards(metrics_service.compute_kpis(df))

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_overview, tab_runs, tab_errors, tab_perf = st.tabs(["Overview", "Run log", "Errors", "Performance"])

with tab_overview:
    overview_tab.render(df)
with tab_runs:
    run_log_tab.render(df)
with tab_errors:
    errors_tab.render(df)
with tab_perf:
    performance_tab.render(df)
