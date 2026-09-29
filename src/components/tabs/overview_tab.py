import pandas as pd
import streamlit as st

from src.components import charts
from src.services import metrics_service
from src.utils.formatting import fmt_duration

_CARD_CLASS = {"SUCCESS": "success", "FAILED": "failed", "TIMEOUT": "failed", "WARNING": "warning"}


def _render_task_cards(df: pd.DataFrame, per_row: int = 4, limit: int = 12) -> None:
    tasks = metrics_service.task_summary(df)
    if tasks.empty:
        return
    st.markdown('<div class="section-eyebrow">Tasks · latest state</div>', unsafe_allow_html=True)
    if len(tasks) > limit and not st.toggle(f"Show all {len(tasks)} tasks", value=False):
        tasks = tasks.head(limit)
    for i in range(0, len(tasks), per_row):
        cols = st.columns(per_row)
        for col, (_, t) in zip(cols, tasks.iloc[i:i + per_row].iterrows()):
            css = _CARD_CLASS.get(t["last_status"], "total")
            col.markdown(
                f"""
                <div class="kpi-card {css}">
                    <div class="kpi-label">{t['PROCESS_NAME']} › {t['TASK_NAME']}</div>
                    <div class="kpi-value sm">{t['last_status']}</div>
                    <div class="kpi-sub">{int(t['runs'])} runs · {t['success_rate']:.0f}% ok · avg {fmt_duration(t['avg_dur'])}</div>
                    <div class="kpi-sub">last {t['last_start']:%m-%d %H:%M}</div>
                </div>""",
                unsafe_allow_html=True,
            )


def render(df: pd.DataFrame) -> None:
    total = len(df)

    _render_task_cards(df)

    st.markdown('<div class="section-eyebrow">Runs over time</div>', unsafe_allow_html=True)
    ts_pivot = metrics_service.runs_over_time(df)
    st.plotly_chart(charts.runs_over_time_chart(ts_pivot), width='stretch')

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="section-eyebrow">Status</div>', unsafe_allow_html=True)
        status_counts = metrics_service.status_distribution(df)
        st.plotly_chart(charts.status_pie(status_counts, total), width='stretch')
    with c2:
        st.markdown('<div class="section-eyebrow">By process type</div>', unsafe_allow_html=True)
        type_stats = metrics_service.stats_by_process_type(df)
        st.plotly_chart(charts.process_type_breakdown(type_stats), width='stretch')
    with c3:
        st.markdown('<div class="section-eyebrow">Top processes</div>', unsafe_allow_html=True)
        top_proc = metrics_service.top_processes_by_run_count(df)
        st.plotly_chart(charts.top_processes_bar(top_proc), width='stretch')