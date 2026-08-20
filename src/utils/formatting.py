"""Small, pure formatting helpers. No Streamlit or IO here on purpose,
so they're trivial to unit test.
"""
from __future__ import annotations

import pandas as pd

from src.config.constants import STATUS_COLORS


def fmt_duration(seconds) -> str:
    """Render a duration in seconds as a short human string ('5m 3s')."""
    if pd.isna(seconds):
        return "—"
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    return f"{seconds // 3600}h {(seconds % 3600) // 60}m"


def fmt_rows(count) -> str:
    """Render a row count with K/M suffixes ('1.2M')."""
    if pd.isna(count):
        return "—"
    count = int(count)
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


def status_pill_html(status: str) -> str:
    """Render a status as a small colored HTML pill (used inside tables/expanders)."""
    css_class = f"pill-{status.lower()}"
    return f'<span class="status-pill {css_class}">{status}</span>'


def status_color(status: str) -> str:
    return STATUS_COLORS.get(status, "#4A5068")
