from datetime import datetime, timedelta

import pandas as pd
import pytest

from src.services.filtering import (
    RunFilters,
    apply_catalog_filters,
    apply_filters,
    apply_search,
    apply_time_window,
    window_start,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    now = datetime(2026, 1, 1, 12, 0, 0)
    return pd.DataFrame([
        dict(PROCESS_NAME="etl_customers", TASK_NAME="extract", PROCESS_TYPE="AIRFLOW",
             STATUS_NAME="SUCCESS", TARGET_TABLE="DWH.FACT_SALES", PROCESS_RUN_ID="run_00001",
             START_TIME=now),
        dict(PROCESS_NAME="etl_products", TASK_NAME="load", PROCESS_TYPE="DBT",
             STATUS_NAME="FAILED", TARGET_TABLE="DWH.DIM_PRODUCTS", PROCESS_RUN_ID="run_00002",
             START_TIME=now - timedelta(hours=48)),
    ])


def test_apply_filters_no_filters_returns_all(sample_df):
    result = apply_filters(sample_df, RunFilters())
    assert len(result) == 2


def test_apply_filters_by_process_type(sample_df):
    result = apply_filters(sample_df, RunFilters(process_types=["AIRFLOW"]))
    assert len(result) == 1
    assert result.iloc[0]["PROCESS_NAME"] == "etl_customers"


def test_apply_filters_by_status(sample_df):
    result = apply_filters(sample_df, RunFilters(statuses=["FAILED"]))
    assert len(result) == 1
    assert result.iloc[0]["STATUS_NAME"] == "FAILED"


def test_apply_time_window_excludes_old_rows(sample_df):
    now = datetime(2026, 1, 1, 12, 0, 0)
    result = apply_time_window(sample_df, "Today", now=now)
    assert len(result) == 1
    assert result.iloc[0]["PROCESS_NAME"] == "etl_customers"


def test_apply_time_window_all_time_returns_everything(sample_df):
    assert len(apply_time_window(sample_df, "All time")) == 2


def test_window_start_presets():
    now = datetime(2026, 1, 10, 15, 30)
    assert window_start("Today", now) == datetime(2026, 1, 10)
    assert window_start("Yesterday + today", now) == datetime(2026, 1, 9)
    assert window_start("1 week", now) == datetime(2026, 1, 3, 15, 30)
    assert window_start("All time", now) is None


def test_apply_search_matches_process_name(sample_df):
    result = apply_search(sample_df, "customers")
    assert len(result) == 1


def test_apply_search_empty_returns_all(sample_df):
    result = apply_search(sample_df, "")
    assert len(result) == 2


def test_apply_catalog_filters_ignores_status():
    catalog = pd.DataFrame([
        dict(PROCESS_NAME="a", TASK_NAME="x", PROCESS_TYPE="AIRFLOW"),
        dict(PROCESS_NAME="b", TASK_NAME="y", PROCESS_TYPE="DBT"),
    ])
    result = apply_catalog_filters(catalog, RunFilters(process_types=["DBT"], statuses=["FAILED"]))
    assert len(result) == 1
    assert result.iloc[0]["PROCESS_NAME"] == "b"
