from src.config.constants import STATUS_NAMES
from src.services.demo_data_service import generate_demo_data


def test_generate_demo_data_row_count():
    df = generate_demo_data(n=50, seed=1)
    assert len(df) == 50


def test_generate_demo_data_is_deterministic():
    df1 = generate_demo_data(n=20, seed=7)
    df2 = generate_demo_data(n=20, seed=7)
    pd_equal = df1.equals(df2)
    assert pd_equal


def test_generate_demo_data_statuses_are_valid():
    df = generate_demo_data(n=100, seed=3)
    assert set(df["STATUS_NAME"].unique()).issubset(set(STATUS_NAMES))


def test_generate_demo_data_success_status_flag_matches_name():
    df = generate_demo_data(n=100, seed=3)
    success_rows = df[df["STATUS_NAME"] == "SUCCESS"]
    other_rows = df[df["STATUS_NAME"] != "SUCCESS"]
    assert (success_rows["STATUS"] == 1).all()
    assert (other_rows["STATUS"] == 0).all()
