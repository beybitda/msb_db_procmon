"""Data-access for the process monitor log table.

This is the only module that contains SQL. The query is parameterized
(bind variable ``:hours``) rather than string-interpolated, so it is not
vulnerable to SQL injection.
"""
from __future__ import annotations

import logging

import pandas as pd

from src.config.settings import AppSettings, OracleSettings
from src.database.connection import OracleConnectionError, oracle_connection

logger = logging.getLogger(__name__)

_TIMESTAMP_COLUMNS = ["START_TIME", "END_TIME", "UPDATED_AT", "INSERTED_AT"]
_NUMERIC_COLUMNS = ["DURATION_SECONDS", "ROWS_PROCESSED", "ATTEMPT_NUMBER", "STATUS", "RUN_ID"]


def _build_query(table_name: str) -> str:
    return f"""
        SELECT
            RUN_ID, PROCESS_RUN_ID, PROCESS_NAME, TASK_NAME, PROCESS_TYPE, TARGET_TABLE,
            START_TIME, END_TIME, DURATION_SECONDS, ATTEMPT_NUMBER,
            STATUS, STATUS_NAME, BUSINESS_DATE, ROWS_PROCESSED,
            DBMS_LOB.SUBSTR(ERROR_MESSAGE, 4000, 1) AS ERROR_MESSAGE,
            DBMS_LOB.SUBSTR(EXTRA_INFO, 4000, 1)    AS EXTRA_INFO,
            UPDATED_AT, INSERTED_AT
        FROM {table_name}
        WHERE START_TIME >= SYSDATE - :hours / 24
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
    hours_back: int = 24,
) -> tuple[pd.DataFrame, str | None]:
    """Fetch process run rows from Oracle for the given lookback window.

    Returns:
        (dataframe, error_message). ``error_message`` is ``None`` on success;
        on failure an empty dataframe is returned alongside a human-readable
        error string so the UI can decide how to degrade gracefully.
    """
    query = _build_query(app_settings.table_name)
    try:
        with oracle_connection(oracle_settings) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, hours=hours_back)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
            finally:
                cursor.close()
        df = pd.DataFrame(rows, columns=columns)
        return _normalize_types(df), None
    except OracleConnectionError as exc:
        logger.warning("Failed to fetch process runs from Oracle: %s", exc)
        return pd.DataFrame(), str(exc)
