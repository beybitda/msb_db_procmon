from datetime import datetime, timedelta

import pandas as pd
import pytest

from src.services import metrics_service


@pytest.fixture
def sample_df() -> pd.DataFrame:
    now = datetime(2026, 1, 1, 12, 0, 0)
    rows = [
        dict(RUN_ID=1, PROCESS_NAME="etl_customers", TASK_NAME="extract", PROCESS_TYPE="AIRFLOW",
             STATUS_NAME="SUCCESS", STATUS=1, START_TIME=now, DURATION_SECONDS=100, ROWS_PROCESSED=1000,
             ERROR_MESSAGE=None),
        dict(RUN_ID=2, PROCESS_NAME="etl_customers", TASK_NAME="load", PROCESS_TYPE="AIRFLOW",
             STATUS_NAME="FAILED", STATUS=0, START_TIME=now - timedelta(hours=1), DURATION_SECONDS=50,
             ROWS_PROCESSED=None, ERROR_MESSAGE="boom"),
        dict(RUN_ID=3, PROCESS_NAME="etl_products", TASK_NAME="extract", PROCESS_TYPE="DBT",
             STATUS_NAME="RUNNING", STATUS=0, START_TIME=now - timedelta(hours=2), DURATION_SECONDS=None,
             ROWS_PROCESSED=None, ERROR_MESSAGE=None),
        dict(RUN_ID=4, PROCESS_NAME="etl_products", TASK_NAME="load", PROCESS_TYPE="DBT",
             STATUS_NAME="WARNING", STATUS=0, START_TIME=now - timedelta(hours=3), DURATION_SECONDS=200,
             ROWS_PROCESSED=500, ERROR_MESSAGE=None),
    ]
    return pd.DataFrame(rows)


def test_compute_kpis(sample_df):
    kpis = metrics_service.compute_kpis(sample_df)
    assert kpis.total == 4
    assert kpis.success == 1
    assert kpis.failed == 1
    assert kpis.running == 1
    assert kpis.warning == 1
    assert kpis.success_rate == pytest.approx(25.0)


def test_compute_kpis_empty_df():
    empty = pd.DataFrame(columns=["STATUS_NAME", "STATUS", "DURATION_SECONDS"])
    kpis = metrics_service.compute_kpis(empty)
    assert kpis.total == 0
    assert kpis.success_rate == 0.0
    assert kpis.avg_duration_seconds is None


def test_status_distribution(sample_df):
    counts = metrics_service.status_distribution(sample_df)
    assert set(counts["Status"]) == {"SUCCESS", "FAILED", "RUNNING", "WARNING"}
    assert counts["Count"].sum() == 4


def test_stats_by_process_type(sample_df):
    stats = metrics_service.stats_by_process_type(sample_df)
    airflow = stats[stats["PROCESS_TYPE"] == "AIRFLOW"].iloc[0]
    assert airflow["total"] == 2
    assert airflow["success"] == 1
    assert airflow["fail"] == 1


def test_top_processes_by_run_count(sample_df):
    top = metrics_service.top_processes_by_run_count(sample_df, limit=5)
    assert set(top["Process"]) == {"etl_customers", "etl_products"}
    assert top["Runs"].sum() == 4


def test_problem_runs(sample_df):
    problems = metrics_service.problem_runs(sample_df)
    assert set(problems["STATUS_NAME"]) == {"FAILED", "WARNING"}


def test_successful_runs_with_duration(sample_df):
    perf = metrics_service.successful_runs_with_duration(sample_df)
    assert len(perf) == 1
    assert perf.iloc[0]["RUN_ID"] == 1


def test_performance_summary(sample_df):
    summary = metrics_service.performance_summary(sample_df)
    assert set(summary.columns) == {
        "PROCESS_NAME", "TASK_NAME", "runs", "success_rate", "avg_dur", "max_dur", "total_rows",
    }
    assert summary["runs"].sum() == 4
