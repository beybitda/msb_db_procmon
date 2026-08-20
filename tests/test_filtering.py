from datetime import datetime, timedelta

import pandas as pd
import pytest

from src.services.filtering import RunFilters, apply_filters, apply_search, apply_time_window


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
    result = apply_time_window(sample_df, hours_back=24, now=now)
    assert len(result) == 1
    assert result.iloc[0]["PROCESS_NAME"] == "etl_customers"


def test_apply_search_matches_process_name(sample_df):
    result = apply_search(sample_df, "customers")
    assert len(result) == 1


def test_apply_search_empty_returns_all(sample_df):
    result = apply_search(sample_df, "")
    assert len(result) == 2
