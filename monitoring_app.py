import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time
from dotenv import load_dotenv

load_dotenv()

# ─── Oracle env config ───────────────────────────────────────────────────────
ORACLE_USER = os.getenv("ORACLE_USER", "")
ORACLE_PASS = os.getenv("ORACLE_PASS", "")
ORACLE_HOST = os.getenv("ORACLE_HOST", "")
ORACLE_PORT = os.getenv("ORACLE_PORT", "1521")
ORACLE_DB   = os.getenv("ORACLE_DB", "")   # service name / SID

ENV_CONFIGURED = all([ORACLE_USER, ORACLE_PASS, ORACLE_HOST, ORACLE_DB])

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Process Monitor",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Theme / CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Background */
.stApp { background-color: #0D0F14; }
section[data-testid="stSidebar"] { background-color: #111318 !important; border-right: 1px solid #1E222D; }

/* Hide default header */
header[data-testid="stHeader"] { background: transparent; }

/* Sidebar text */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span { color: #7A8099 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.08em; }

section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stMultiSelect > div > div { background-color: #1A1D26 !important; border: 1px solid #2A2E3D !important; color: #C8CCDB !important; }

/* KPI cards */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }
.kpi-card {
    background: #111318;
    border: 1px solid #1E222D;
    border-radius: 4px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-card.success::before { background: #00D4A0; }
.kpi-card.failed::before  { background: #FF4757; }
.kpi-card.warning::before { background: #FFB627; }
.kpi-card.total::before   { background: #4A9EFF; }

.kpi-label { color: #4A5068; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; font-family: 'IBM Plex Mono', monospace; margin-bottom: 8px; }
.kpi-value { color: #E8EAF0; font-size: 32px; font-weight: 300; font-family: 'IBM Plex Mono', monospace; line-height: 1; }
.kpi-sub   { color: #3D4258; font-size: 11px; margin-top: 4px; }

/* Section headers */
.section-eyebrow {
    color: #4A5068;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-family: 'IBM Plex Mono', monospace;
    border-left: 2px solid #4A9EFF;
    padding-left: 10px;
    margin: 32px 0 16px;
}

/* Status pills */
.status-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 2px;
    font-size: 10px;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.05em;
}
.pill-success  { background: rgba(0,212,160,0.12); color: #00D4A0; border: 1px solid rgba(0,212,160,0.25); }
.pill-failed   { background: rgba(255,71,87,0.12);  color: #FF4757; border: 1px solid rgba(255,71,87,0.25); }
.pill-running  { background: rgba(74,158,255,0.12); color: #4A9EFF; border: 1px solid rgba(74,158,255,0.25); }
.pill-warning  { background: rgba(255,182,39,0.12); color: #FFB627; border: 1px solid rgba(255,182,39,0.25); }
.pill-skipped  { background: rgba(122,128,153,0.12);color: #7A8099; border: 1px solid rgba(122,128,153,0.25); }
.pill-timeout  { background: rgba(255,107,53,0.12); color: #FF6B35; border: 1px solid rgba(255,107,53,0.25); }
.pill-retrying { background: rgba(168,85,247,0.12); color: #A855F7; border: 1px solid rgba(168,85,247,0.25); }
.pill-created  { background: rgba(74,158,255,0.08); color: #4A9EFF; border: 1px solid rgba(74,158,255,0.15); }
.pill-cancelled{ background: rgba(122,128,153,0.12);color: #7A8099; border: 1px solid rgba(122,128,153,0.2); }

/* Table styling */
.stDataFrame { border: 1px solid #1E222D !important; border-radius: 4px; }
.stDataFrame thead th { background-color: #111318 !important; color: #4A5068 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 10px !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; border-bottom: 1px solid #1E222D !important; }
.stDataFrame tbody td { color: #C8CCDB !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 12px !important; border-bottom: 1px solid #1A1D26 !important; background-color: #0D0F14 !important; }
.stDataFrame tbody tr:hover td { background-color: #111318 !important; }

/* App title */
.app-header { padding: 8px 0 24px; border-bottom: 1px solid #1E222D; margin-bottom: 0; }
.app-title { color: #E8EAF0; font-size: 22px; font-weight: 500; letter-spacing: -0.01em; }
.app-subtitle { color: #4A5068; font-size: 12px; font-family: 'IBM Plex Mono', monospace; margin-top: 2px; }

/* Refresh indicator */
.refresh-dot {
    display: inline-block;
    width: 6px; height: 6px;
    background: #00D4A0;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* Error detail box */
.error-box {
    background: rgba(255,71,87,0.06);
    border: 1px solid rgba(255,71,87,0.2);
    border-radius: 4px;
    padding: 12px 16px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #FF4757;
    margin: 8px 0;
    white-space: pre-wrap;
    word-break: break-all;
}

/* Sidebar logo */
.sidebar-logo {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    color: #4A9EFF;
    letter-spacing: 0.05em;
    padding: 16px 0 24px;
    border-bottom: 1px solid #1E222D;
    margin-bottom: 20px;
}

div[data-testid="stMetric"] { background: #111318; border: 1px solid #1E222D; border-radius: 4px; padding: 16px; }
div[data-testid="stMetric"] label { color: #4A5068 !important; font-size: 10px !important; text-transform: uppercase; letter-spacing: 0.1em; font-family: 'IBM Plex Mono', monospace; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #E8EAF0 !important; font-family: 'IBM Plex Mono', monospace; }

/* Plotly charts background */
.js-plotly-plot .plotly .bg { fill: #111318 !important; }

/* Button */
.stButton button {
    background-color: #1A1D26 !important;
    color: #C8CCDB !important;
    border: 1px solid #2A2E3D !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.05em !important;
    border-radius: 3px !important;
}
.stButton button:hover {
    border-color: #4A9EFF !important;
    color: #4A9EFF !important;
}

div[data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid #1E222D; gap: 0; }
div[data-baseweb="tab"] { background: transparent !important; color: #4A5068 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.08em; padding: 8px 20px !important; border-radius: 0 !important; }
div[data-baseweb="tab"][aria-selected="true"] { color: #4A9EFF !important; border-bottom: 2px solid #4A9EFF !important; }
</style>
""", unsafe_allow_html=True)


# ─── Mock data generator ────────────────────────────────────────────────────
PROCESS_TYPES = ["AIRFLOW", "INFORMATICA", "SERVICE", "DBT", "SPARK"]
PROCESS_NAMES = [
    "etl_customers_daily", "etl_transactions_hourly", "etl_products_sync",
    "report_revenue_monthly", "load_crm_data", "sync_inventory",
    "aggregate_kpi_daily", "cleanup_temp_tables", "validate_data_quality",
    "export_to_datalake", "ingest_raw_events", "transform_user_sessions",
]
TABLES = [
    "DWH.FACT_SALES", "DWH.DIM_CUSTOMERS", "DWH.FACT_TRANSACTIONS",
    "STG.RAW_EVENTS", "RPT.REVENUE_SUMMARY", "DWH.FACT_INVENTORY",
    "STG.CRM_CONTACTS", "RPT.KPI_DASHBOARD", "DWH.DIM_PRODUCTS",
]
STATUS_NAMES = ["SUCCESS", "FAILED", "RUNNING", "WARNING", "SKIPPED", "RETRYING", "TIMEOUT", "CREATED", "CANCELLED"]
ERROR_MSGS = [
    "ORA-01017: invalid username/password; logon denied",
    "Connection timed out after 30000ms",
    "Table DWH.FACT_SALES does not exist or insufficient privileges",
    "Deadlock detected during insert operation",
    "Memory limit exceeded: required 8GB, available 2GB",
    None, None, None,
]


@st.cache_data(ttl=30)
def generate_data(n=200, seed=42):
    random.seed(seed)
    now = datetime.now()
    rows = []
    for i in range(1, n + 1):
        status_name = random.choices(
            STATUS_NAMES,
            weights=[40, 10, 8, 7, 5, 5, 3, 10, 4],
            k=1,
        )[0]
        status = 1 if status_name == "SUCCESS" else 0
        start = now - timedelta(hours=random.randint(0, 168), minutes=random.randint(0, 59))
        duration = random.randint(5, 7200) if status_name not in ("CREATED",) else None
        end = (start + timedelta(seconds=duration)) if duration and status_name not in ("RUNNING", "RETRYING", "CREATED") else None
        rows.append({
            "RUN_ID": i,
            "PROCESS_RUN_ID": f"run_{i:05d}_{random.randint(10000,99999)}",
            "PROCESS_NAME": random.choice(PROCESS_NAMES),
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
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=30)
def load_oracle_data(hours_back: int = 24) -> tuple[pd.DataFrame, str | None]:
    """Fetch data from Oracle using env-based credentials. Returns (df, error)."""
    try:
        import oracledb
    except ImportError:
        return pd.DataFrame(), "oracledb package not installed. Run: pip install oracledb"

    dsn = f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_DB}"
    try:
        conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=dsn)
        query = """
            SELECT
                RUN_ID, PROCESS_RUN_ID, PROCESS_NAME, TASK_NAME, PROCESS_TYPE, TARGET_TABLE,
                START_TIME, END_TIME, DURATION_SECONDS, ATTEMPT_NUMBER,
                STATUS, STATUS_NAME, BUSINESS_DATE, ROWS_PROCESSED,
                DBMS_LOB.SUBSTR(ERROR_MESSAGE, 4000, 1) AS ERROR_MESSAGE,
                DBMS_LOB.SUBSTR(EXTRA_INFO, 4000, 1)    AS EXTRA_INFO,
                UPDATED_AT, INSERTED_AT
            FROM ANALYST_MSB2.MSB_DB_PROCESS_MONITOR
            WHERE START_TIME >= SYSDATE - :hours / 24
            ORDER BY START_TIME DESC
        """
        df = pd.read_sql(query, conn, params={"hours": hours_back})
        conn.close()
        df.columns = [c.upper() for c in df.columns]
        # Normalise types
        for col in ["START_TIME", "END_TIME", "UPDATED_AT", "INSERTED_AT"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        for col in ["DURATION_SECONDS", "ROWS_PROCESSED", "ATTEMPT_NUMBER", "STATUS", "RUN_ID"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df, None
    except Exception as exc:
        return pd.DataFrame(), str(exc)


# ─── Helpers ─────────────────────────────────────────────────────────────────
STATUS_COLORS = {
    "SUCCESS": "#00D4A0", "FAILED": "#FF4757", "RUNNING": "#4A9EFF",
    "WARNING": "#FFB627", "SKIPPED": "#7A8099", "RETRYING": "#A855F7",
    "TIMEOUT": "#FF6B35", "CREATED": "#4A9EFF", "CANCELLED": "#7A8099",
}

def pill(status: str) -> str:
    cls = f"pill-{status.lower()}"
    return f'<span class="status-pill {cls}">{status}</span>'


def fmt_duration(sec) -> str:
    if pd.isna(sec):
        return "—"
    sec = int(sec)
    if sec < 60:
        return f"{sec}s"
    if sec < 3600:
        return f"{sec//60}m {sec%60}s"
    return f"{sec//3600}h {(sec%3600)//60}m"


def fmt_rows(n) -> str:
    if pd.isna(n):
        return "—"
    n = int(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">⬡ PROC·MON</div>', unsafe_allow_html=True)

    st.markdown("**CONNECTION**")
    if ENV_CONFIGURED:
        st.markdown(
            f'<div style="color:#00D4A0;font-family:\'IBM Plex Mono\',monospace;font-size:10px;">'
            f'⬤ ENV  {ORACLE_USER}@{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_DB}</div>',
            unsafe_allow_html=True,
        )
        conn_mode = st.radio(
            "Data source",
            ["Oracle DB", "Demo data"],
            label_visibility="collapsed",
        )
    else:
        st.markdown(
            '<div style="color:#4A5068;font-family:\'IBM Plex Mono\',monospace;font-size:10px;">'
            '○ ENV not set — using demo data</div>',
            unsafe_allow_html=True,
        )
        conn_mode = "Demo data"

    st.divider()
    st.markdown("**FILTERS**")

    # ── Pre-load to populate filter options ──────────────────────────────────
    _oracle_error = None
    if conn_mode == "Oracle DB":
        with st.spinner("Connecting…"):
            df_all, _oracle_error = load_oracle_data(hours_back=168)
        if _oracle_error or df_all.empty:
            st.error(f"Oracle error — falling back to demo data\n{_oracle_error or 'empty result'}")
            conn_mode = "Demo data"

    if conn_mode == "Demo data":
        df_all = generate_data(300)

    proc_types = st.multiselect(
        "Process type",
        options=sorted(df_all["PROCESS_TYPE"].unique()),
        default=[],
        placeholder="All types",
    )
    proc_names = st.multiselect(
        "Process name",
        options=sorted(df_all["PROCESS_NAME"].unique()),
        default=[],
        placeholder="All processes",
    )
    task_names = st.multiselect(
        "Task name",
        options=sorted(df_all["TASK_NAME"].unique()),
        default=[],
        placeholder="All tasks",
    )
    statuses = st.multiselect(
        "Status",
        options=STATUS_NAMES,
        default=[],
        placeholder="All statuses",
    )

    hours_back = st.select_slider(
        "Time window",
        options=[1, 3, 6, 12, 24, 48, 72, 168],
        value=24,
        format_func=lambda h: f"Last {h}h" if h < 168 else "Last 7d",
    )

    st.divider()
    auto_refresh = st.toggle("Auto-refresh (30s)", value=False)
    if st.button("↺  Refresh now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ─── Filter data ─────────────────────────────────────────────────────────────
# For Oracle, re-fetch scoped to the chosen time window (query handles it);
# for demo data, slice the in-memory frame.
if conn_mode == "Oracle DB":
    df, _err = load_oracle_data(hours_back=hours_back)
    if _err or df.empty:
        df = df_all.copy()  # graceful fallback
else:
    df = df_all.copy()
    cutoff = datetime.now() - timedelta(hours=hours_back)
    df = df[df["START_TIME"] >= cutoff]

if proc_types:
    df = df[df["PROCESS_TYPE"].isin(proc_types)]
if proc_names:
    df = df[df["PROCESS_NAME"].isin(proc_names)]
if task_names:
    df = df[df["TASK_NAME"].isin(task_names)]
if statuses:
    df = df[df["STATUS_NAME"].isin(statuses)]


# ─── Auto-refresh ─────────────────────────────────────────────────────────────
if auto_refresh:
    time.sleep(30)
    st.rerun()


# ─── Header ──────────────────────────────────────────────────────────────────
col_title, col_ts = st.columns([3, 1])
with col_title:
    st.markdown("""
    <div class="app-header">
        <div class="app-title">Process Monitor</div>
        <div class="app-subtitle">ETL · AIRFLOW · INFORMATICA · SERVICE</div>
    </div>
    """, unsafe_allow_html=True)
with col_ts:
    st.markdown(f"""
    <div style="text-align:right; padding-top:16px">
        <div style="color:#4A5068; font-size:10px; font-family:'IBM Plex Mono',monospace; letter-spacing:0.08em">LAST UPDATED</div>
        <div style="color:#C8CCDB; font-size:12px; font-family:'IBM Plex Mono',monospace">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        <div style="margin-top:4px"><span class="refresh-dot"></span><span style="color:#00D4A0; font-size:10px; font-family:'IBM Plex Mono',monospace">LIVE</span></div>
    </div>
    """, unsafe_allow_html=True)


# ─── KPI cards ───────────────────────────────────────────────────────────────
total = len(df)
n_success = (df["STATUS_NAME"] == "SUCCESS").sum()
n_failed  = (df["STATUS_NAME"] == "FAILED").sum()
n_running = (df["STATUS_NAME"].isin(["RUNNING", "RETRYING"])).sum()
n_warn    = (df["STATUS_NAME"] == "WARNING").sum()
sr = (n_success / total * 100) if total else 0
avg_dur   = df["DURATION_SECONDS"].mean()

st.markdown("""
<div class="kpi-grid">
""", unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""
    <div class="kpi-card total">
        <div class="kpi-label">Total runs</div>
        <div class="kpi-value">{total}</div>
        <div class="kpi-sub">in window</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-card success">
        <div class="kpi-label">Success rate</div>
        <div class="kpi-value">{sr:.1f}%</div>
        <div class="kpi-sub">{n_success} completed</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi-card failed">
        <div class="kpi-label">Failed</div>
        <div class="kpi-value">{n_failed}</div>
        <div class="kpi-sub">requires attention</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""
    <div class="kpi-card warning">
        <div class="kpi-label">In progress</div>
        <div class="kpi-value">{n_running}</div>
        <div class="kpi-sub">{n_warn} with warnings</div>
    </div>""", unsafe_allow_html=True)
with k5:
    st.markdown(f"""
    <div class="kpi-card total">
        <div class="kpi-label">Avg duration</div>
        <div class="kpi-value">{fmt_duration(avg_dur)}</div>
        <div class="kpi-sub">per run</div>
    </div>""", unsafe_allow_html=True)


# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_overview, tab_runs, tab_errors, tab_perf = st.tabs(["Overview", "Run log", "Errors", "Performance"])

CHART_LAYOUT = dict(
    paper_bgcolor="#111318",
    plot_bgcolor="#0D0F14",
    font=dict(family="IBM Plex Mono", color="#7A8099", size=10),
    margin=dict(l=0, r=0, t=8, b=0),
)
AXIS_STYLE = dict(
    xaxis=dict(gridcolor="#1E222D", linecolor="#1E222D", tickfont=dict(size=9)),
    yaxis=dict(gridcolor="#1E222D", linecolor="#1E222D", tickfont=dict(size=9)),
)

# ── Tab 1: Overview ──────────────────────────────────────────────────────────
with tab_overview:
    c1, c2 = st.columns([1, 2])

    with c1:
        st.markdown('<div class="section-eyebrow">Status distribution</div>', unsafe_allow_html=True)
        status_counts = df["STATUS_NAME"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        colors = [STATUS_COLORS.get(s, "#4A5068") for s in status_counts["Status"]]
        fig_pie = go.Figure(go.Pie(
            labels=status_counts["Status"],
            values=status_counts["Count"],
            hole=0.65,
            marker=dict(colors=colors, line=dict(color="#0D0F14", width=2)),
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value} runs (%{percent})<extra></extra>",
        ))
        fig_pie.add_annotation(
            text=f"<b>{total}</b><br><span style='font-size:10px'>runs</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="#E8EAF0", family="IBM Plex Mono"),
        )
        fig_pie.update_layout(**CHART_LAYOUT, **AXIS_STYLE, height=260, showlegend=True,
                               legend=dict(orientation="v", x=1.0, y=0.5,
                                           font=dict(size=10, color="#7A8099"),
                                           bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.markdown('<div class="section-eyebrow">Runs over time</div>', unsafe_allow_html=True)
        df_time = df.copy()
        df_time["hour"] = df_time["START_TIME"].dt.floor("h")
        ts = df_time.groupby(["hour", "STATUS_NAME"]).size().reset_index(name="count")
        ts_pivot = ts.pivot(index="hour", columns="STATUS_NAME", values="count").fillna(0)

        fig_ts = go.Figure()
        for s in ["SUCCESS", "FAILED", "WARNING", "RUNNING", "SKIPPED", "RETRYING", "TIMEOUT"]:
            if s in ts_pivot.columns:
                fig_ts.add_trace(go.Bar(
                    name=s, x=ts_pivot.index, y=ts_pivot[s],
                    marker_color=STATUS_COLORS.get(s, "#4A5068"),
                    hovertemplate=f"<b>{s}</b> %{{y}}<extra></extra>",
                ))
        fig_ts.update_layout(**CHART_LAYOUT, **AXIS_STYLE, barmode="stack", height=260,
                              legend=dict(orientation="h", y=-0.15, font=dict(size=9), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_ts, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="section-eyebrow">By process type</div>', unsafe_allow_html=True)
        type_stats = df.groupby("PROCESS_TYPE").agg(
            total=("RUN_ID", "count"),
            success=("STATUS", "sum"),
        ).reset_index()
        type_stats["fail"] = type_stats["total"] - type_stats["success"]
        type_stats["sr"] = (type_stats["success"] / type_stats["total"] * 100).round(1)
        fig_type = go.Figure()
        fig_type.add_trace(go.Bar(name="Success", x=type_stats["PROCESS_TYPE"], y=type_stats["success"],
                                   marker_color="#00D4A0", hovertemplate="%{y}<extra>Success</extra>"))
        fig_type.add_trace(go.Bar(name="Failed/Other", x=type_stats["PROCESS_TYPE"], y=type_stats["fail"],
                                   marker_color="#FF4757", hovertemplate="%{y}<extra>Failed</extra>"))
        fig_type.update_layout(**CHART_LAYOUT, **AXIS_STYLE, barmode="stack", height=220,
                                legend=dict(orientation="h", y=-0.2, bgcolor="rgba(0,0,0,0)", font=dict(size=9)))
        st.plotly_chart(fig_type, use_container_width=True)

    with c4:
        st.markdown('<div class="section-eyebrow">Top processes by run count</div>', unsafe_allow_html=True)
        top_proc = df["PROCESS_NAME"].value_counts().head(8).reset_index()
        top_proc.columns = ["Process", "Runs"]
        fig_bar = go.Figure(go.Bar(
            x=top_proc["Runs"], y=top_proc["Process"],
            orientation="h",
            marker=dict(color=top_proc["Runs"], colorscale=[[0, "#1E222D"], [1, "#4A9EFF"]]),
            hovertemplate="<b>%{y}</b><br>%{x} runs<extra></extra>",
        ))
        fig_bar.update_layout(**CHART_LAYOUT, **AXIS_STYLE, height=220,
                        yaxis_autorange="reversed")
        st.plotly_chart(fig_bar, use_container_width=True)


# ── Tab 2: Run log ───────────────────────────────────────────────────────────
with tab_runs:
    st.markdown('<div class="section-eyebrow">All runs</div>', unsafe_allow_html=True)

    col_s, col_t, col_n = st.columns([2, 1, 1])
    with col_s:
        search = st.text_input("Search process name / table / run ID", placeholder="etl_customers...", label_visibility="collapsed")
    with col_t:
        sort_col = st.selectbox("Sort by", ["START_TIME", "DURATION_SECONDS", "ROWS_PROCESSED", "RUN_ID"],
                                 label_visibility="collapsed")
    with col_n:
        sort_asc = st.toggle("Ascending", value=False)

    dfd = df.copy()
    if search:
        mask = (
            dfd["PROCESS_NAME"].str.contains(search, case=False, na=False) |
            dfd["TARGET_TABLE"].str.contains(search, case=False, na=False) |
            dfd["PROCESS_RUN_ID"].str.contains(search, case=False, na=False)
        )
        dfd = dfd[mask]

    dfd = dfd.sort_values(sort_col, ascending=sort_asc)

    display_cols = ["RUN_ID", "PROCESS_NAME", "TASK_NAME", "PROCESS_TYPE", "TARGET_TABLE",
                "STATUS_NAME", "START_TIME", "DURATION_SECONDS", "ROWS_PROCESSED",
                "ATTEMPT_NUMBER", "BUSINESS_DATE"]
    dfd_show = dfd[display_cols].copy()
    dfd_show["START_TIME"] = dfd_show["START_TIME"].dt.strftime("%Y-%m-%d %H:%M")
    dfd_show["DURATION_SECONDS"] = dfd_show["DURATION_SECONDS"].apply(fmt_duration)
    dfd_show["ROWS_PROCESSED"] = dfd_show["ROWS_PROCESSED"].apply(fmt_rows)
    dfd_show.columns = ["ID", "Process", "Task", "Type", "Table", "Status",
                     "Started", "Duration", "Rows", "Attempt", "Biz date"]

    st.dataframe(
        dfd_show,
        use_container_width=True,
        height=420,
        hide_index=True,
        column_config={
            "Status": st.column_config.Column(width="small"),
            "Type": st.column_config.Column(width="small"),
            "Attempt": st.column_config.Column(width="small"),
        }
    )
    st.caption(f"{len(dfd_show):,} records shown")


# ── Tab 3: Errors ───────────────────────────────────────────────────────────
with tab_errors:
    st.markdown('<div class="section-eyebrow">Failed & problem runs</div>', unsafe_allow_html=True)

    err_df = df[df["STATUS_NAME"].isin(["FAILED", "TIMEOUT", "WARNING"])].copy()
    err_df = err_df.sort_values("START_TIME", ascending=False)

    if err_df.empty:
        st.markdown('<div style="color:#4A5068; font-family:\'IBM Plex Mono\',monospace; font-size:12px; padding:32px 0;">No failures in selected window.</div>', unsafe_allow_html=True)
    else:
        for _, row in err_df.head(30).iterrows():
            with st.expander(f"[{row['STATUS_NAME']}]  {row['PROCESS_NAME']} › {row['TASK_NAME']}  ·  {row['START_TIME'].strftime('%Y-%m-%d %H:%M')}"):
                ec1, ec2, ec3 = st.columns(3)
                ec1.markdown(f"**Run ID:** `{row['RUN_ID']}`")
                ec1.markdown(f"**Type:** `{row['PROCESS_TYPE']}`")
                ec1.markdown(f"**Task:** `{row['TASK_NAME']}`")
                ec2.markdown(f"**Table:** `{row['TARGET_TABLE']}`")
                ec2.markdown(f"**Duration:** `{fmt_duration(row['DURATION_SECONDS'])}`")
                ec3.markdown(f"**Attempt:** `{int(row['ATTEMPT_NUMBER']) if pd.notna(row['ATTEMPT_NUMBER']) else '—'}`")
                ec3.markdown(f"**Biz date:** `{row['BUSINESS_DATE']}`")

                if row["ERROR_MESSAGE"]:
                    st.markdown('<div style="color:#4A5068; font-size:10px; text-transform:uppercase; letter-spacing:0.08em; margin-top:8px">Error message</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="error-box">{row["ERROR_MESSAGE"]}</div>', unsafe_allow_html=True)

                if row["EXTRA_INFO"]:
                    st.markdown('<div style="color:#4A5068; font-size:10px; text-transform:uppercase; letter-spacing:0.08em; margin-top:8px">Extra info</div>', unsafe_allow_html=True)
                    st.code(str(row["EXTRA_INFO"]), language="json")

    st.markdown('<div class="section-eyebrow">Error frequency by process</div>', unsafe_allow_html=True)
    if not err_df.empty:
        err_freq = err_df.groupby(["PROCESS_NAME", "TASK_NAME", "STATUS_NAME"]).size().reset_index(name="count")
        fig_err = px.bar(err_freq, x="TASK_NAME", y="count", color="STATUS_NAME",
                        facet_col="PROCESS_NAME",
                        labels={"TASK_NAME": "", "count": "Occurrences", "STATUS_NAME": "Status"})
        fig_err.update_layout(**CHART_LAYOUT, **AXIS_STYLE, height=250,
                                    xaxis_tickangle=-30,
                                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)))
        st.plotly_chart(fig_err, use_container_width=True)


# ── Tab 4: Performance ───────────────────────────────────────────────────────
with tab_perf:
    st.markdown('<div class="section-eyebrow">Duration distribution</div>', unsafe_allow_html=True)

    perf_df = df[df["DURATION_SECONDS"].notna() & (df["STATUS_NAME"] == "SUCCESS")].copy()

    pc1, pc2 = st.columns(2)
    with pc1:
        fig_hist = px.histogram(perf_df, x="DURATION_SECONDS", nbins=40,
                                 color_discrete_sequence=["#4A9EFF"],
                                 labels={"DURATION_SECONDS": "Duration (seconds)", "count": "Runs"})
        fig_hist.update_layout(**CHART_LAYOUT, **AXIS_STYLE, height=230)
        fig_hist.update_traces(marker_line_color="#0D0F14", marker_line_width=0.5)
        st.plotly_chart(fig_hist, use_container_width=True)

    with pc2:
        dur_by_proc = perf_df.groupby(["PROCESS_NAME", "TASK_NAME"])["DURATION_SECONDS"].agg(["mean", "max", "min"]).reset_index()
        dur_by_proc.columns = ["Process", "Task", "Avg (s)", "Max (s)", "Min (s)"]
        dur_by_proc = dur_by_proc.sort_values("Avg (s)", ascending=False).head(10)
        fig_box = px.bar(dur_by_proc, x="Task", y="Avg (s)",
                          color="Process",
                          color_discrete_sequence=["#4A9EFF"],
                          error_y=dur_by_proc["Max (s)"] - dur_by_proc["Avg (s)"],
                          labels={"Avg (s)": "Avg duration (s)"})
        fig_box.update_layout(**CHART_LAYOUT, **AXIS_STYLE, height=230,
                               xaxis_tickangle=-30)
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown('<div class="section-eyebrow">Rows processed over time</div>', unsafe_allow_html=True)
    rows_df = df[df["ROWS_PROCESSED"].notna()].copy()
    rows_df["hour"] = rows_df["START_TIME"].dt.floor("h")
    rows_ts = rows_df.groupby("hour")["ROWS_PROCESSED"].sum().reset_index()
    fig_rows = go.Figure(go.Scatter(
        x=rows_ts["hour"], y=rows_ts["ROWS_PROCESSED"],
        mode="lines",
        line=dict(color="#00D4A0", width=1.5),
        fill="tozeroy",
        fillcolor="rgba(0,212,160,0.06)",
        hovertemplate="%{x}<br><b>%{y:,.0f}</b> rows<extra></extra>",
    ))
    fig_rows.update_layout(**CHART_LAYOUT, **AXIS_STYLE, height=200,
                            yaxis_tickformat=",.0f")
    st.plotly_chart(fig_rows, use_container_width=True)

    st.markdown('<div class="section-eyebrow">Process performance summary</div>', unsafe_allow_html=True)
    perf_summary = df.groupby(["PROCESS_NAME", "TASK_NAME"]).agg(
        runs=("RUN_ID", "count"),
        success_rate=("STATUS", "mean"),
        avg_dur=("DURATION_SECONDS", "mean"),
        max_dur=("DURATION_SECONDS", "max"),
        total_rows=("ROWS_PROCESSED", "sum"),
    ).reset_index()
    perf_summary["success_rate"] = (perf_summary["success_rate"] * 100).round(1)
    perf_summary["avg_dur"] = perf_summary["avg_dur"].apply(fmt_duration)
    perf_summary["max_dur"] = perf_summary["max_dur"].apply(fmt_duration)
    perf_summary["total_rows"] = perf_summary["total_rows"].apply(fmt_rows)
    perf_summary.columns = ["Process", "Task", "Runs", "SR %", "Avg dur", "Max dur", "Total rows"]
    perf_summary = perf_summary.sort_values("Runs", ascending=False)
    st.dataframe(perf_summary, use_container_width=True, hide_index=True, height=300)