import pandas as pd

from src.utils.formatting import fmt_duration, fmt_rows, status_color, status_pill_html


def test_fmt_duration_seconds():
    assert fmt_duration(45) == "45s"


def test_fmt_duration_minutes():
    assert fmt_duration(125) == "2m 5s"


def test_fmt_duration_hours():
    assert fmt_duration(3725) == "1h 2m"


def test_fmt_duration_nan():
    assert fmt_duration(pd.NA) == "—"
    assert fmt_duration(float("nan")) == "—"


def test_fmt_rows_small():
    assert fmt_rows(42) == "42"


def test_fmt_rows_thousands():
    assert fmt_rows(4_200) == "4.2K"


def test_fmt_rows_millions():
    assert fmt_rows(2_500_000) == "2.5M"


def test_fmt_rows_nan():
    assert fmt_rows(pd.NA) == "—"


def test_status_pill_html_contains_status_and_css_class():
    html = status_pill_html("FAILED")
    assert "FAILED" in html
    assert "pill-failed" in html


def test_status_color_known_and_unknown():
    assert status_color("SUCCESS") == "#00D4A0"
    assert status_color("NOT_A_REAL_STATUS") == "#4A5068"
