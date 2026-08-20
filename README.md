# MSB DB Process Monitor

Streamlit dashboard for monitoring ETL and data pipeline executions stored in an Oracle table.

---

## Table of contents

- [Features](#features)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Table schema](#table-schema)
- [Requirements](#requirements)
- [Environment variables](#environment-variables)
- [Running locally](#running-locally)
- [Docker](#docker)
- [Testing](#testing)
- [Deployment notes](#deployment-notes)

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

## Architecture

The app follows a simple layered structure so UI, business logic, and data
access don't bleed into each other:

```
app.py (entry point)
  → src/components   (Streamlit rendering: sidebar, KPI cards, charts, tabs)
      → src/services  (pure business logic: filtering, metrics, data orchestration)
          → src/database (SQL + Oracle connection handling)
      → src/config    (settings & constants, loaded from env)
      → src/utils     (formatting helpers)
      → src/models    (typed data holders, e.g. KPIMetrics)
```

Key ideas:

- **`app.py` is a thin entry point.** It wires page config → sidebar → data
  loading → filtering → tab rendering. No business logic lives here.
- **No SQL outside `src/database`.** The single query lives in
  `process_run_repository.py`, using a bind variable (`:hours`), not string
  interpolation.
- **Services are pure functions.** `metrics_service.py` and `filtering.py`
  take a dataframe in and return a dataframe/dataclass out — no Streamlit
  imports — so they're trivial to unit test (see `tests/`).
- **Caching lives at the service boundary.** `st.cache_data` is applied in
  `data_service.py` and `demo_data_service.py`, not scattered across the UI.
- **Credentials never touch source code.** `src/config/settings.py` is the
  only place that reads `os.getenv`; everything else receives typed
  `OracleSettings` / `AppSettings` objects.

---

## Project structure

```
.
├── app.py                          # Streamlit entry point
├── src/
│   ├── config/
│   │   ├── settings.py             # OracleSettings / AppSettings, env loading
│   │   └── constants.py            # Status vocab, colors, demo vocab, column layout
│   ├── database/
│   │   ├── connection.py           # Oracle connection context manager + error type
│   │   └── repositories/
│   │       └── process_run_repository.py   # The one place with SQL
│   ├── services/
│   │   ├── data_service.py         # Picks Oracle vs demo source, applies caching
│   │   ├── demo_data_service.py    # Synthetic data generator (demo mode)
│   │   ├── filtering.py            # Sidebar filter application (pure)
│   │   └── metrics_service.py      # KPI + chart-data aggregations (pure)
│   ├── components/
│   │   ├── styles.py               # Custom CSS theme
│   │   ├── header.py                # Title + live timestamp
│   │   ├── kpi_cards.py             # 5-card KPI row
│   │   ├── charts.py                # Plotly figure builders
│   │   ├── sidebar.py               # Connection status, filters, refresh
│   │   └── tabs/
│   │       ├── overview_tab.py
│   │       ├── run_log_tab.py
│   │       ├── errors_tab.py
│   │       └── performance_tab.py
│   ├── models/
│   │   └── metrics.py              # KPIMetrics dataclass
│   └── utils/
│       └── formatting.py           # fmt_duration, fmt_rows, status_pill_html
├── tests/                          # pytest suite for services/utils
├── .streamlit/
│   └── config.toml                 # Dark theme + server settings
├── requirements.txt
├── requirements-dev.txt            # + pytest, for running tests
├── Dockerfile
├── docker-compose.yml
├── .env.example                    # Placeholder credentials — copy to .env
├── .gitignore
└── README.md
```

---

## Table schema

The app reads from `ANALYST_MSB2.MSB_DB_PROCESS_MONITOR`:

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

## Requirements

- Python 3.12+
- Oracle DB accessible from the host (for live data — optional, demo mode works without it)

Runtime packages (see `requirements.txt`):

```
streamlit>=1.35.0
pandas>=2.0.0
plotly>=5.20.0
oracledb>=2.0.0
python-dotenv>=1.0.0
```

---

## Environment variables

Copy `.env.example` to `.env` and fill in your Oracle credentials:

```dotenv
ORACLE_USER=your_username
ORACLE_PASS=your_password
ORACLE_HOST=your_host.example.com
ORACLE_PORT=1521
ORACLE_DB=your_service_name
```

If any of these are missing, the app starts in **demo mode** with synthetic
data — no Oracle connection is attempted. `.env` is git-ignored; never
commit real credentials.

---

## Running locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the app
streamlit run app.py --server.port 8502
```

Open `http://localhost:8502` in your browser.

---

## Docker

```bash
docker compose up --build
```

The compose file expects a `.env` three directories up from this project
(`../../../.env`), matching the original deployment layout — adjust the
`env_file` path if you relocate the project.

---

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

Tests cover the pure logic layers — `formatting`, `filtering`,
`metrics_service`, and `demo_data_service` — since these hold the actual
business rules. UI rendering (`src/components`) and Oracle I/O
(`src/database`) are intentionally left out of automated tests, since they
require a live Streamlit runtime or a real database respectively; keeping
the business logic pure is what makes it testable without either.

---

## Deployment notes

- The app is stateless per Streamlit session; horizontal scaling behind a
  load balancer works as long as sessions are sticky (Streamlit's default
  websocket-based session model requires this).
- `st.cache_data(ttl=30)` on data loading means Oracle is queried at most
  once per 30 seconds per unique set of call arguments, not on every
  rerun/filter change.
- Auto-refresh (`time.sleep` + `st.rerun`) blocks that session's server
  thread for the sleep duration — fine at low concurrency, but worth
  revisiting (e.g. client-side polling) if many users enable it
  simultaneously.
