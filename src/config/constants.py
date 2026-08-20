"""Static, non-configurable constants used across the app.

These never change at runtime and are safe to import from anywhere
(UI components, services, tests) without triggering side effects.
"""

# ─── Domain vocab (also used by the demo data generator) ───────────────────
PROCESS_TYPES = ["AIRFLOW", "INFORMATICA", "SERVICE", "DBT", "SPARK"]

PROCESS_NAMES = [
    "etl_customers", "etl_transactions", "etl_products",
    "report_revenue", "load_crm", "sync_inventory",
    "aggregate_kpi", "cleanup_temp", "validate_quality",
    "export_datalake", "ingest_events", "transform_sessions",
]

TASK_NAMES = ["extract", "transform", "load", "validate", "notify", "cleanup"]

TABLES = [
    "DWH.FACT_SALES", "DWH.DIM_CUSTOMERS", "DWH.FACT_TRANSACTIONS",
    "STG.RAW_EVENTS", "RPT.REVENUE_SUMMARY", "DWH.FACT_INVENTORY",
    "STG.CRM_CONTACTS", "RPT.KPI_DASHBOARD", "DWH.DIM_PRODUCTS",
]

ERROR_MSGS = [
    "ORA-01017: invalid username/password; logon denied",
    "Connection timed out after 30000ms",
    "Table DWH.FACT_SALES does not exist or insufficient privileges",
    "Deadlock detected during insert operation",
    "Memory limit exceeded: required 8GB, available 2GB",
    None, None, None,
]

# ─── Status vocabulary (drives filters, pills, charts) ──────────────────────
STATUS_NAMES = [
    "SUCCESS", "FAILED", "RUNNING", "WARNING", "SKIPPED",
    "RETRYING", "TIMEOUT", "CREATED", "CANCELLED",
]

# Relative weights used only by the synthetic demo data generator.
STATUS_DEMO_WEIGHTS = [40, 10, 8, 7, 5, 5, 3, 10, 4]

STATUS_COLORS = {
    "SUCCESS": "#00D4A0", "FAILED": "#FF4757", "RUNNING": "#4A9EFF",
    "WARNING": "#FFB627", "SKIPPED": "#7A8099", "RETRYING": "#A855F7",
    "TIMEOUT": "#FF6B35", "CREATED": "#4A9EFF", "CANCELLED": "#7A8099",
}

# Statuses considered "in progress" for KPI purposes.
RUNNING_STATUSES = ["RUNNING", "RETRYING"]

# Statuses considered failures/problems for the Errors tab.
PROBLEM_STATUSES = ["FAILED", "TIMEOUT", "WARNING"]

# ─── Column layout for the Run log tab ──────────────────────────────────────
RUN_LOG_COLUMNS = [
    "RUN_ID", "PROCESS_NAME", "TASK_NAME", "PROCESS_TYPE", "TARGET_TABLE",
    "STATUS_NAME", "START_TIME", "DURATION_SECONDS", "ROWS_PROCESSED",
    "ATTEMPT_NUMBER", "BUSINESS_DATE",
]
RUN_LOG_COLUMN_LABELS = [
    "ID", "Process", "Task", "Type", "Table", "Status",
    "Started", "Duration", "Rows", "Attempt", "Biz date",
]

TIME_WINDOW_OPTIONS = [1, 3, 6, 12, 24, 48, 72, 168]
DEFAULT_TIME_WINDOW_HOURS = 24
