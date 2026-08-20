"""Generates synthetic process-run data for demo mode.

Isolated from the Oracle repository so the two data sources share the same
downstream shape (columns, dtypes) without either module knowing about the
other.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from src.config.constants import (
    ERROR_MSGS,
    PROCESS_NAMES,
    PROCESS_TYPES,
    STATUS_DEMO_WEIGHTS,
    STATUS_NAMES,
    TABLES,
    TASK_NAMES,
)
from src.config.settings import AppSettings


def _generate_row(i: int, now: datetime) -> dict:
    status_name = random.choices(STATUS_NAMES, weights=STATUS_DEMO_WEIGHTS, k=1)[0]
    status = 1 if status_name == "SUCCESS" else 0
    start = now - timedelta(hours=random.randint(0, 168), minutes=random.randint(0, 59))
    duration = random.randint(5, 7200) if status_name != "CREATED" else None
    is_open_ended = status_name in ("RUNNING", "RETRYING", "CREATED")
    end = (start + timedelta(seconds=duration)) if duration and not is_open_ended else None

    return {
        "RUN_ID": i,
        "PROCESS_RUN_ID": f"run_{i:05d}_{random.randint(10000, 99999)}",
        "PROCESS_NAME": random.choice(PROCESS_NAMES),
        "TASK_NAME": random.choice(TASK_NAMES),
        "PROCESS_TYPE": random.choice(PROCESS_TYPES),
        "TARGET_TABLE": random.choice(TABLES),
        "START_TIME": start,
        "END_TIME": end,
        "DURATION_SECONDS": duration,
        "ATTEMPT_NUMBER": random.choice([1, 1, 1, 2, 3]),
        "STATUS": status,
        "STATUS_NAME": status_name,
        "BUSINESS_DATE": (start - timedelta(days=random.randint(0, 2))).date(),
        "ROWS_PROCESSED": random.randint(0, 5_000_000) if status_name == "SUCCESS" else None,
        "ERROR_MESSAGE": random.choice(ERROR_MSGS) if status_name in ("FAILED", "TIMEOUT") else None,
        "EXTRA_INFO": '{"dag_id":"' + random.choice(PROCESS_NAMES) + '","executor":"LocalExecutor"}',
        "UPDATED_AT": end or start,
        "INSERTED_AT": start,
    }


@st.cache_data(ttl=30)
def generate_demo_data(n: int = 300, seed: int = 42) -> pd.DataFrame:
    """Deterministic (seeded) synthetic dataset shaped like the Oracle table."""
    random.seed(seed)
    now = datetime.now()
    rows = [_generate_row(i, now) for i in range(1, n + 1)]
    return pd.DataFrame(rows)


def generate_demo_data_with_settings(app_settings: AppSettings) -> pd.DataFrame:
    return generate_demo_data(n=app_settings.demo_row_count)
