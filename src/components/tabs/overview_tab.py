import pandas as pd
import streamlit as st

from src.components import charts
from src.services import metrics_service


def render(df: pd.DataFrame) -> None:
    total = len(df)
    c1, c2 = st.columns([1, 2])

    with c1:
        st.markdown('<div class="section-eyebrow">Status distribution</div>', unsafe_allow_html=True)
        status_counts = metrics_service.status_distribution(df)
        st.plotly_chart(charts.status_pie(status_counts, total), width='stretch')

    with c2:
        st.markdown('<div class="section-eyebrow">Runs over time</div>', unsafe_allow_html=True)
        ts_pivot = metrics_service.runs_over_time(df)
        st.plotly_chart(charts.runs_over_time_chart(ts_pivot), width='stretch')

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="section-eyebrow">By process type</div>', unsafe_allow_html=True)
        type_stats = metrics_service.stats_by_process_type(df)
        st.plotly_chart(charts.process_type_breakdown(type_stats), width='stretch')

    with c4:
        st.markdown('<div class="section-eyebrow">Top processes by run count</div>', unsafe_allow_html=True)
        top_proc = metrics_service.top_processes_by_run_count(df)
        st.plotly_chart(charts.top_processes_bar(top_proc), width='stretch')
