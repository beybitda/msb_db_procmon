"""Pure data-transformation functions that feed the KPI cards and charts.

Kept free of Streamlit/Plotly so they can be unit tested with plain
dataframes in, dataframes/dataclasses out.
"""
from __future__ import annotations

import pandas as pd

from src.config.constants import PROBLEM_STATUSES, RUNNING_STATUSES
from src.models.metrics import KPIMetrics


def compute_kpis(df: pd.DataFrame) -> KPIMetrics:
    total = len(df)
    n_success = int((df["STATUS_NAME"] == "SUCCESS").sum())
    n_failed = int((df["STATUS_NAME"] == "FAILED").sum())
    n_running = int(df["STATUS_NAME"].isin(RUNNING_STATUSES).sum())
    n_warning = int((df["STATUS_NAME"] == "WARNING").sum())
    success_rate = (n_success / total * 100) if total else 0.0
    avg_duration = df["DURATION_SECONDS"].mean() if total else None
    return KPIMetrics(
        total=total,
        success=n_success,
        failed=n_failed,
        running=n_running,
        warning=n_warning,
        success_rate=success_rate,
        avg_duration_seconds=avg_duration,
    )


def status_distribution(df: pd.DataFrame) -> pd.DataFrame:
    counts = df["STATUS_NAME"].value_counts().reset_index()
    counts.columns = ["Status", "Count"]
    return counts


def runs_over_time(df: pd.DataFrame) -> pd.DataFrame:
    """Hourly run counts per status, pivoted (hour x status -> count)."""
    df_time = df.copy()
    df_time["hour"] = df_time["START_TIME"].dt.floor("h")
    ts = df_time.groupby(["hour", "STATUS_NAME"]).size().reset_index(name="count")
    return ts.pivot(index="hour", columns="STATUS_NAME", values="count").fillna(0)


def stats_by_process_type(df: pd.DataFrame) -> pd.DataFrame:
    stats = df.groupby("PROCESS_TYPE").agg(
        total=("RUN_ID", "count"),
        success=("STATUS", "sum"),
    ).reset_index()
    stats["fail"] = stats["total"] - stats["success"]
    stats["sr"] = (stats["success"] / stats["total"] * 100).round(1)
    return stats


def top_processes_by_run_count(df: pd.DataFrame, limit: int = 8) -> pd.DataFrame:
    top = df["PROCESS_NAME"].value_counts().head(limit).reset_index()
    top.columns = ["Process", "Runs"]
    return top


def problem_runs(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["STATUS_NAME"].isin(PROBLEM_STATUSES)].sort_values("START_TIME", ascending=False)


def error_frequency(df_problems: pd.DataFrame) -> pd.DataFrame:
    return (
        df_problems.groupby(["PROCESS_NAME", "TASK_NAME", "STATUS_NAME"])
        .size()
        .reset_index(name="count")
    )


def successful_runs_with_duration(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["DURATION_SECONDS"].notna() & (df["STATUS_NAME"] == "SUCCESS")].copy()


def duration_by_process_task(perf_df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    grouped = (
        perf_df.groupby(["PROCESS_NAME", "TASK_NAME"])["DURATION_SECONDS"]
        .agg(["mean", "max", "min"])
        .reset_index()
    )
    grouped.columns = ["Process", "Task", "Avg (s)", "Max (s)", "Min (s)"]
    return grouped.sort_values("Avg (s)", ascending=False).head(limit)


def rows_processed_over_time(df: pd.DataFrame) -> pd.DataFrame:
    rows_df = df[df["ROWS_PROCESSED"].notna()].copy()
    rows_df["hour"] = rows_df["START_TIME"].dt.floor("h")
    return rows_df.groupby("hour")["ROWS_PROCESSED"].sum().reset_index()


def performance_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby(["PROCESS_NAME", "TASK_NAME"]).agg(
        runs=("RUN_ID", "count"),
        success_rate=("STATUS", "mean"),
        avg_dur=("DURATION_SECONDS", "mean"),
        max_dur=("DURATION_SECONDS", "max"),
        total_rows=("ROWS_PROCESSED", "sum"),
    ).reset_index()
    summary["success_rate"] = (summary["success_rate"] * 100).round(1)
    return summary.sort_values("runs", ascending=False)
