import pandas as pd
import streamlit as st

from src.services import metrics_service
from src.utils.formatting import fmt_duration

_COLOR_SUCCESS = "#00D4A0"
_COLOR_FAILED = "#FF4757"
_COLOR_NOT_STARTED = "#FFB627"


def _task_color(today_status) -> str:
    if pd.isna(today_status):
        return _COLOR_NOT_STARTED
    if today_status == "SUCCESS":
        return _COLOR_SUCCESS
    return _COLOR_FAILED


def _task_row_html(t: pd.Series) -> str:
    color = _task_color(t["today_status"])
    last = f"{t['last_start']:%m-%d %H:%M}" if pd.notna(t["last_start"]) else "—"
    if int(t["runs"]) == 0:
        meta = f"0 runs · — ok · avg — · last {last}"
    else:
        meta = f"{int(t['runs'])} runs · {t['success_rate']:.0f}% ok · avg {fmt_duration(t['avg_dur'])} · last {last}"
    return f"""
    <div class="task-row">
        <span class="task-dot" style="background:{color}"></span>
        <span class="task-name">{t['TASK_NAME']}</span>
        <span class="task-meta">{meta}</span>
    </div>"""


def _render_process_group(proc_name: str, tasks: pd.DataFrame) -> None:
    rows_html = "".join(_task_row_html(t) for _, t in tasks.iterrows())
    st.markdown(
        f"""
        <div class="proc-group">
            <div class="proc-group-title">{proc_name}</div>
            {rows_html}
        </div>""",
        unsafe_allow_html=True,
    )


def _render_task_groups(df: pd.DataFrame, catalog: pd.DataFrame | None) -> None:
    tasks = metrics_service.task_summary(df, catalog)
    if tasks.empty:
        return

    st.markdown('<div class="section-eyebrow">Tasks · latest state</div>', unsafe_allow_html=True)

    # Processes ordered by their most recent START_TIME; tasks within a
    # process keep that same ordering (task_summary already sorts by last_start desc).
    proc_order = tasks.groupby("PROCESS_NAME", sort=False)["last_start"].max().sort_values(ascending=False).index
    groups = tasks.groupby("PROCESS_NAME", sort=False)

    col1, col2 = st.columns(2)
    for i, proc_name in enumerate(proc_order):
        with (col1 if i % 2 == 0 else col2):
            _render_process_group(proc_name, groups.get_group(proc_name))


def render(df: pd.DataFrame, catalog: pd.DataFrame | None = None) -> None:
    _render_task_groups(df, catalog)
