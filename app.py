"""Process Monitor — Streamlit entry point.

This file only wires things together: page config, sidebar, data
filtering, and tab rendering. All business logic lives in ``src/``.
"""
import streamlit as st

from src.components import header, kpi_cards
from src.components.sidebar import render_sidebar
from src.components.styles import inject_custom_css
from src.components.tabs import errors_tab, overview_tab, performance_tab, run_log_tab
from src.config.settings import get_app_settings, get_oracle_settings
from src.services import metrics_service
from src.services.data_service import load_data
from src.services.filtering import apply_filters

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


def dashboard() -> None:
    # Re-fetch here (not sidebar.df_all) so timed refreshes actually pick up new rows.
    df, _ = load_data(sidebar.source, oracle_settings, app_settings, sidebar.window)
    if df.empty:
        df = sidebar.df_all
    df = apply_filters(df, sidebar.filters)

    header.render_header()
    if df.empty:
        st.info("No runs in the selected window.")
        return
    kpi_cards.render_kpi_cards(metrics_service.compute_kpis(df))

    tab_overview, tab_runs, tab_errors, tab_perf = st.tabs(["Overview", "Run log", "Errors", "Performance"])
    with tab_overview:
        overview_tab.render(df)
    with tab_runs:
        run_log_tab.render(df)
    with tab_errors:
        errors_tab.render(df)
    with tab_perf:
        performance_tab.render(df)


# Only this fragment re-runs on the timer, so the page never blocks.
run_every = app_settings.auto_refresh_seconds if sidebar.auto_refresh else None
st.fragment(run_every=run_every)(dashboard)()