"""Renders the 5-card KPI row at the top of the dashboard."""
import streamlit as st

from src.models.metrics import KPIMetrics
from src.utils.formatting import fmt_duration


def render_kpi_cards(metrics: KPIMetrics) -> None:
    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(
            f"""
            <div class="kpi-card total">
                <div class="kpi-label">Total runs</div>
                <div class="kpi-value">{metrics.total}</div>
                <div class="kpi-sub">in window</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""
            <div class="kpi-card success">
                <div class="kpi-label">Success rate</div>
                <div class="kpi-value">{metrics.success_rate:.1f}%</div>
                <div class="kpi-sub">{metrics.success} completed</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""
            <div class="kpi-card failed">
                <div class="kpi-label">Failed</div>
                <div class="kpi-value">{metrics.failed}</div>
                <div class="kpi-sub">requires attention</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f"""
            <div class="kpi-card warning">
                <div class="kpi-label">In progress</div>
                <div class="kpi-value">{metrics.running}</div>
                <div class="kpi-sub">{metrics.warning} with warnings</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with k5:
        st.markdown(
            f"""
            <div class="kpi-card total">
                <div class="kpi-label">Avg duration</div>
                <div class="kpi-value">{fmt_duration(metrics.avg_duration_seconds)}</div>
                <div class="kpi-sub">per run</div>
            </div>""",
            unsafe_allow_html=True,
        )
