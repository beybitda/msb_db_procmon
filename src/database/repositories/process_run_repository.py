"""Data-access for the process monitor log table.

This is the only module that contains SQL. The query is parameterized
(bind variable ``:since``) rather than string-interpolated, so it is not
vulnerable to SQL injection.
"""
from __future__ import annotations

import logging
from datetime import datetime

import pandas as pd

from src.config.settings import AppSettings, OracleSettings
from src.database.connection import OracleConnectionError, oracle_connection

logger = logging.getLogger(__name__)

_TIMESTAMP_COLUMNS = ["START_TIME", "END_TIME", "UPDATED_AT", "INSERTED_AT"]
_NUMERIC_COLUMNS = ["DURATION_SECONDS", "ROWS_PROCESSED", "ATTEMPT_NUMBER", "STATUS", "RUN_ID"]


def _build_query(table_name: str, bounded: bool) -> str:
    where = "WHERE START_TIME >= :since" if bounded else ""
    return f"""
        SELECT
            RUN_ID, PROCESS_RUN_ID, PROCESS_NAME, TASK_NAME, PROCESS_TYPE, TARGET_TABLE,
            START_TIME, END_TIME, DURATION_SECONDS, ATTEMPT_NUMBER,
            STATUS, STATUS_NAME, BUSINESS_DATE, ROWS_PROCESSED,
            DBMS_LOB.SUBSTR(ERROR_MESSAGE, 4000, 1) AS ERROR_MESSAGE,
            DBMS_LOB.SUBSTR(EXTRA_INFO, 4000, 1)    AS EXTRA_INFO,
            UPDATED_AT, INSERTED_AT
        FROM {table_name}
        {where}
        ORDER BY START_TIME DESC
    """


def _normalize_types(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.upper() for c in df.columns]
    for col in _TIMESTAMP_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in _NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def fetch_process_runs(
    oracle_settings: OracleSettings,
    app_settings: AppSettings,
    since: datetime | None = None,
) -> tuple[pd.DataFrame, str | None]:
    """Fetch process run rows from Oracle starting at ``since`` (None = all time).

    Returns:
        (dataframe, error_message). ``error_message`` is ``None`` on success;
        on failure an empty dataframe is returned alongside a human-readable
        error string so the UI can decide how to degrade gracefully.
    """
    query = _build_query(app_settings.table_name, bounded=since is not None)
    params = {"since": since} if since is not None else {}
    try:
        with oracle_connection(oracle_settings) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
            finally:
                cursor.close()
        df = pd.DataFrame(rows, columns=columns)
        return _normalize_types(df), None
    except OracleConnectionError as exc:
        logger.warning("Failed to fetch process runs from Oracle: %s", exc)
        return pd.DataFrame(), str(exc)


def fetch_task_catalog(
    oracle_settings: OracleSettings,
    app_settings: AppSettings,
) -> tuple[pd.DataFrame, str | None]:
    """All distinct (process, task, type) ever seen + their latest START_TIME."""
    query = f"""
        SELECT PROCESS_NAME, TASK_NAME, PROCESS_TYPE, MAX(START_TIME) AS LAST_START
        FROM {app_settings.table_name}
        GROUP BY PROCESS_NAME, TASK_NAME, PROCESS_TYPE
    """
    try:
        with oracle_connection(oracle_settings) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                columns = [c[0].upper() for c in cursor.description]
                rows = cursor.fetchall()
            finally:
                cursor.close()
        df = pd.DataFrame(rows, columns=columns)
        df["LAST_START"] = pd.to_datetime(df["LAST_START"], errors="coerce")
        return df, None
    except OracleConnectionError as exc:
        logger.warning("Failed to fetch task catalog from Oracle: %s", exc)
        return pd.DataFrame(), str(exc)