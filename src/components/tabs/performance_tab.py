import pandas as pd
import streamlit as st

from src.components import charts
from src.services import metrics_service
from src.utils.formatting import fmt_duration, fmt_rows


def render(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-eyebrow">Duration distribution</div>', unsafe_allow_html=True)

    perf_df = metrics_service.successful_runs_with_duration(df)

    pc1, pc2 = st.columns(2)
    with pc1:
        st.plotly_chart(charts.duration_histogram(perf_df), width='stretch')
    with pc2:
        dur_by_proc = metrics_service.duration_by_process_task(perf_df)
        st.plotly_chart(charts.duration_by_task_chart(dur_by_proc), width='stretch')

    st.markdown('<div class="section-eyebrow">Rows processed over time</div>', unsafe_allow_html=True)
    rows_ts = metrics_service.rows_processed_over_time(df)
    st.plotly_chart(charts.rows_processed_chart(rows_ts), width='stretch')

    st.markdown('<div class="section-eyebrow">Process performance summary</div>', unsafe_allow_html=True)
    summary = metrics_service.performance_summary(df)
    display = summary.copy()
    display["avg_dur"] = display["avg_dur"].apply(fmt_duration)
    display["max_dur"] = display["max_dur"].apply(fmt_duration)
    display["total_rows"] = display["total_rows"].apply(fmt_rows)
    display.columns = ["Process", "Task", "Runs", "SR %", "Avg dur", "Max dur", "Total rows"]
    st.dataframe(display, width='stretch', hide_index=True, height=300)
