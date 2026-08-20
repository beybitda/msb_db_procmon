import pandas as pd
import streamlit as st

from src.config.constants import RUN_LOG_COLUMN_LABELS, RUN_LOG_COLUMNS
from src.services.filtering import apply_search
from src.utils.formatting import fmt_duration, fmt_rows


def render(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-eyebrow">All runs</div>', unsafe_allow_html=True)

    col_s, col_t, col_n = st.columns([2, 1, 1])
    with col_s:
        search = st.text_input(
            "Search process name / table / run ID",
            placeholder="etl_customers...",
            label_visibility="collapsed",
        )
    with col_t:
        sort_col = st.selectbox(
            "Sort by", ["START_TIME", "DURATION_SECONDS", "ROWS_PROCESSED", "RUN_ID"],
            label_visibility="collapsed",
        )
    with col_n:
        sort_asc = st.toggle("Ascending", value=False)

    filtered = apply_search(df.copy(), search)
    filtered = filtered.sort_values(sort_col, ascending=sort_asc)

    display = filtered[RUN_LOG_COLUMNS].copy()
    display["START_TIME"] = display["START_TIME"].dt.strftime("%Y-%m-%d %H:%M")
    display["DURATION_SECONDS"] = display["DURATION_SECONDS"].apply(fmt_duration)
    display["ROWS_PROCESSED"] = display["ROWS_PROCESSED"].apply(fmt_rows)
    display.columns = RUN_LOG_COLUMN_LABELS

    st.dataframe(
        display,
        width='stretch',
        height=420,
        hide_index=True,
        column_config={
            "Status": st.column_config.Column(width="small"),
            "Type": st.column_config.Column(width="small"),
            "Attempt": st.column_config.Column(width="small"),
        },
    )
    st.caption(f"{len(display):,} records shown")
