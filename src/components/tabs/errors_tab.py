import pandas as pd
import streamlit as st

from src.components import charts
from src.services import metrics_service
from src.utils.formatting import fmt_duration


def _render_error_panel(row: pd.Series) -> None:
    label = f"[{row['STATUS_NAME']}]  {row['PROCESS_NAME']} › {row['TASK_NAME']}  ·  {row['START_TIME'].strftime('%Y-%m-%d %H:%M')}"
    with st.expander(label):
        ec1, ec2, ec3 = st.columns(3)
        ec1.markdown(f"**Run ID:** `{row['RUN_ID']}`")
        ec1.markdown(f"**Type:** `{row['PROCESS_TYPE']}`")
        ec1.markdown(f"**Task:** `{row['TASK_NAME']}`")
        ec2.markdown(f"**Table:** `{row['TARGET_TABLE']}`")
        ec2.markdown(f"**Duration:** `{fmt_duration(row['DURATION_SECONDS'])}`")
        ec3.markdown(f"**Attempt:** `{int(row['ATTEMPT_NUMBER']) if pd.notna(row['ATTEMPT_NUMBER']) else '—'}`")
        ec3.markdown(f"**Biz date:** `{row['BUSINESS_DATE']}`")

        if row["ERROR_MESSAGE"]:
            st.markdown(
                '<div style="color:#4A5068; font-size:10px; text-transform:uppercase; letter-spacing:0.08em; margin-top:8px">Error message</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f'<div class="error-box">{row["ERROR_MESSAGE"]}</div>', unsafe_allow_html=True)

        if row["EXTRA_INFO"]:
            st.markdown(
                '<div style="color:#4A5068; font-size:10px; text-transform:uppercase; letter-spacing:0.08em; margin-top:8px">Extra info</div>',
                unsafe_allow_html=True,
            )
            st.code(str(row["EXTRA_INFO"]), language="json")


def render(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-eyebrow">Failed & problem runs</div>', unsafe_allow_html=True)

    err_df = metrics_service.problem_runs(df)

    if err_df.empty:
        st.markdown(
            '<div style="color:#4A5068; font-family:\'IBM Plex Mono\',monospace; font-size:12px; padding:32px 0;">No failures in selected window.</div>',
            unsafe_allow_html=True,
        )
    else:
        for _, row in err_df.head(30).iterrows():
            _render_error_panel(row)

    st.markdown('<div class="section-eyebrow">Error frequency by process</div>', unsafe_allow_html=True)
    if not err_df.empty:
        err_freq = metrics_service.error_frequency(err_df)
        st.plotly_chart(charts.error_frequency_chart(err_freq), width='stretch')
