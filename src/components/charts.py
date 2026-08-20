"""Plotly figure builders.

Each function takes already-aggregated data (from ``metrics_service``) and
returns a ``go.Figure``/``px`` figure. No data transformation happens here
and no ``st.plotly_chart`` calls either — rendering stays in the tab
components so these builders are easy to unit test or reuse.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.utils.formatting import status_color

CHART_LAYOUT = dict(
    paper_bgcolor="#111318",
    plot_bgcolor="#0D0F14",
    font=dict(family="IBM Plex Mono", color="#7A8099", size=10),
    margin=dict(l=0, r=0, t=8, b=0),
)
AXIS_STYLE = dict(
    xaxis=dict(gridcolor="#1E222D", linecolor="#1E222D", tickfont=dict(size=9)),
    yaxis=dict(gridcolor="#1E222D", linecolor="#1E222D", tickfont=dict(size=9)),
)

_STACKED_STATUS_ORDER = ["SUCCESS", "FAILED", "WARNING", "RUNNING", "SKIPPED", "RETRYING", "TIMEOUT"]


def status_pie(status_counts: pd.DataFrame, total: int) -> go.Figure:
    colors = [status_color(s) for s in status_counts["Status"]]
    fig = go.Figure(go.Pie(
        labels=status_counts["Status"],
        values=status_counts["Count"],
        hole=0.65,
        marker=dict(colors=colors, line=dict(color="#0D0F14", width=2)),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value} runs (%{percent})<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>{total}</b><br><span style='font-size:10px'>runs</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="#E8EAF0", family="IBM Plex Mono"),
    )
    fig.update_layout(
        **CHART_LAYOUT, **AXIS_STYLE, height=260, showlegend=True,
        legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=10, color="#7A8099"), bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def runs_over_time_chart(ts_pivot: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for status in _STACKED_STATUS_ORDER:
        if status in ts_pivot.columns:
            fig.add_trace(go.Bar(
                name=status, x=ts_pivot.index, y=ts_pivot[status],
                marker_color=status_color(status),
                hovertemplate=f"<b>{status}</b> %{{y}}<extra></extra>",
            ))
    fig.update_layout(
        **CHART_LAYOUT, **AXIS_STYLE, barmode="stack", height=260,
        legend=dict(orientation="h", y=-0.15, font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def process_type_breakdown(type_stats: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Success", x=type_stats["PROCESS_TYPE"], y=type_stats["success"],
        marker_color="#00D4A0", hovertemplate="%{y}<extra>Success</extra>",
    ))
    fig.add_trace(go.Bar(
        name="Failed/Other", x=type_stats["PROCESS_TYPE"], y=type_stats["fail"],
        marker_color="#FF4757", hovertemplate="%{y}<extra>Failed</extra>",
    ))
    fig.update_layout(
        **CHART_LAYOUT, **AXIS_STYLE, barmode="stack", height=220,
        legend=dict(orientation="h", y=-0.2, bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
    )
    return fig


def top_processes_bar(top_proc: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=top_proc["Runs"], y=top_proc["Process"],
        orientation="h",
        marker=dict(color=top_proc["Runs"], colorscale=[[0, "#1E222D"], [1, "#4A9EFF"]]),
        hovertemplate="<b>%{y}</b><br>%{x} runs<extra></extra>",
    ))
    fig.update_layout(**CHART_LAYOUT, **AXIS_STYLE, height=220, yaxis_autorange="reversed")
    return fig


def error_frequency_chart(err_freq: pd.DataFrame):
    fig = px.bar(
        err_freq, x="TASK_NAME", y="count", color="STATUS_NAME",
        facet_col="PROCESS_NAME",
        labels={"TASK_NAME": "", "count": "Occurrences", "STATUS_NAME": "Status"},
    )
    fig.update_layout(
        **CHART_LAYOUT, **AXIS_STYLE, height=250, xaxis_tickangle=-30,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
    )
    return fig


def duration_histogram(perf_df: pd.DataFrame):
    fig = px.histogram(
        perf_df, x="DURATION_SECONDS", nbins=40,
        color_discrete_sequence=["#4A9EFF"],
        labels={"DURATION_SECONDS": "Duration (seconds)", "count": "Runs"},
    )
    fig.update_layout(**CHART_LAYOUT, **AXIS_STYLE, height=230)
    fig.update_traces(marker_line_color="#0D0F14", marker_line_width=0.5)
    return fig


def duration_by_task_chart(dur_by_proc: pd.DataFrame):
    fig = px.bar(
        dur_by_proc, x="Task", y="Avg (s)",
        color="Process",
        color_discrete_sequence=["#4A9EFF"],
        error_y=dur_by_proc["Max (s)"] - dur_by_proc["Avg (s)"],
        labels={"Avg (s)": "Avg duration (s)"},
    )
    fig.update_layout(**CHART_LAYOUT, **AXIS_STYLE, height=230, xaxis_tickangle=-30)
    return fig


def rows_processed_chart(rows_ts: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=rows_ts["hour"], y=rows_ts["ROWS_PROCESSED"],
        mode="lines",
        line=dict(color="#00D4A0", width=1.5),
        fill="tozeroy",
        fillcolor="rgba(0,212,160,0.06)",
        hovertemplate="%{x}<br><b>%{y:,.0f}</b> rows<extra></extra>",
    ))
    fig.update_layout(**CHART_LAYOUT, **AXIS_STYLE, height=200, yaxis_tickformat=",.0f")
    return fig
