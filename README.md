# MSB DB Process Monitor

Streamlit dashboard for monitoring ETL and data pipeline executions stored in an Oracle table.

---

## Table of contents

- [Features](#features)
- [Table schema](#table-schema)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Configuration](#configuration)
- [Running locally](#running-locally)

---

## Features

- **Overview** — status distribution donut, hourly run timeline, breakdown by process type, top processes by run count
- **Run log** — searchable and sortable table of all runs with human-readable duration and row counts
- **Errors** — expandable panels for failed/timeout/warning runs with error messages and extra info; error frequency chart per process
- **Performance** — duration histogram, avg/max duration per process, rows-processed timeline, full performance summary table
- **Filters** — process type, process name, task name, status, time window (1h → 7d)
- **Auto-refresh** — optional 30-second auto-refresh toggle
- **Demo mode** — runs with synthetic data when Oracle env vars are not set

---

## Table schema

The app reads from `PROCESS_MONITOR_LOG`:

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | `RUN_ID` | NUMBER | Unique run identifier |
| 2 | `PROCESS_RUN_ID` | VARCHAR2(500) | External run ID (dag_run_id, workflow_run_id, etc.) |
| 3 | `PROCESS_NAME` | VARCHAR2(500) | DAG / workflow name |
| 4 | `TASK_NAME` | VARCHAR2(500) | Task name within the process |
| 5 | `PROCESS_TYPE` | VARCHAR2(50) | AIRFLOW, INFORMATICA, SERVICE, DBT, SPARK, etc. |
| 6 | `TARGET_TABLE` | VARCHAR2(255) | Target table being processed |
| 7 | `START_TIME` | TIMESTAMP(6) | Process start time |
| 8 | `END_TIME` | TIMESTAMP(6) | Process end time |
| 9 | `DURATION_SECONDS` | NUMBER | Execution duration in seconds |
| 10 | `ATTEMPT_NUMBER` | NUMBER | Retry attempt number |
| 11 | `STATUS` | NUMBER | 1 = SUCCESS, 0 = any other |
| 12 | `STATUS_NAME` | VARCHAR2(20) | CREATED, RUNNING, SUCCESS, FAILED, WARNING, SKIPPED, RETRYING, TIMEOUT, CANCELLED |
| 13 | `BUSINESS_DATE` | DATE | Business date of processed data |
| 14 | `ROWS_PROCESSED` | NUMBER | Number of rows processed |
| 15 | `ERROR_MESSAGE` | CLOB | Error text on failure |
| 16 | `EXTRA_INFO` | CLOB | Additional info (JSON, run params, etc.) |
| 17 | `UPDATED_AT` | TIMESTAMP(6) | Last update time |
| 18 | `INSERTED_AT` | TIMESTAMP(6) | Record creation time |

---

## Project structure

```
.
├── monitoring_app.py     # Streamlit application
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container image definition
├── docker-compose.yml    # Compose configuration
├── .env                  # Environment variables (not committed)
└── README.md
```

---

## Requirements

- Python 3.12+
- Oracle DB accessible from the host (for live data)

Python packages (see `requirements.txt`):

```
streamlit>=1.35.0
pandas>=2.0.0
plotly>=5.20.0
oracledb>=2.0.0
python-dotenv>=1.0.0
```

---

## Configuration

Copy `.env` and fill in your Oracle credentials:

```dotenv
ORACLE_USER=your_username
ORACLE_PASS=your_password
ORACLE_HOST=your_host.example.com
ORACLE_PORT=1521
ORACLE_DB=your_service_name
```

If any of these are missing the app starts in **demo mode** with synthetic data — no Oracle connection is attempted.

---

## Running locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the app
streamlit run monitoring_app.py --server.port 8502
```

Open `http://localhost:8502` in your browser.