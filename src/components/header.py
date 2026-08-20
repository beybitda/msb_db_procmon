"""Top-of-page header: app title and a live 'last updated' indicator."""
from datetime import datetime

import streamlit as st


def render_header() -> None:
    col_title, col_ts = st.columns([3, 1])
    with col_title:
        st.markdown(
            """
            <div class="app-header">
                <div class="app-title">Process Monitor</div>
                <div class="app-subtitle">ETL · AIRFLOW · INFORMATICA · SERVICE</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_ts:
        st.markdown(
            f"""
            <div style="text-align:right; padding-top:16px">
                <div style="color:#4A5068; font-size:10px; font-family:'IBM Plex Mono',monospace; letter-spacing:0.08em">LAST UPDATED</div>
                <div style="color:#C8CCDB; font-size:12px; font-family:'IBM Plex Mono',monospace">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                <div style="margin-top:4px"><span class="refresh-dot"></span><span style="color:#00D4A0; font-size:10px; font-family:'IBM Plex Mono',monospace">LIVE</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
