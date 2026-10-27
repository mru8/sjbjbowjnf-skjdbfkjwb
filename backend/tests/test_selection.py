import pandas as pd

from app.selection import select_forecast_at_cutoff

TARGET = "2026-01-15 12:00"  #delivery hr, its cutoff is 14 Jan 09:50

def make_df(rows):
    """rows: list of (publishTime, startTime, generation)."""
    df = pd.DataFrame(rows, columns=["publishTime", "startTime", "generation"])
    df["publishTime"] = pd.to_datetime(df["publishTime"], utc=True)
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
    return df

def test_forecast_published_after_cutoff_is_ignored():
    df = make_df([
        ("2026-01-14 09:30", TARGET, 100),
        ("2026-01-14 11:30", TARGET, 200), #newer but too late
    ])
    result = select_forecast_at_cutoff(df, "09:50")
    assert len(result) == 1
    assert result.loc[0, "generation"] == 100

def test_forecast_published_exactly_at_cutoff_is_allowed():
    df = make_df([
        ("2026-01-14 07:30", TARGET, 100),
        ("2026-01-14 09:50", TARGET, 300),
    ])

    result = select_forecast_at_cutoff(df, "09:50")
    assert result.loc[0, "generation"] == 300

def test_latest_allowed_forecast_wins():
    df = make_df([
        ("2026-01-14 02:30", TARGET, 50),
        ("2026-01-14 07:30", TARGET, 80),
        ("2026-01-14 09:30", TARGET, 100),
    ])
    result = select_forecast_at_cutoff(df, "09:50")
    assert result.loc[0, "generation"] == 100

def test_hour_with_no_allowed_forecast_is_left_out():
    df = make_df([
        ("2026-01-14 11:30", TARGET, 200),  #only a too late forecast exists
    ])
    result = select_forecast_at_cutoff(df, "09:50")
    assert len(result) == 0

def test_forecast_from_two_days_before_is_still_allowed():
    df = make_df([
        ("2026-01-13 22:30", TARGET, 70),  #published on D - 2
    ])
    result = select_forecast_at_cutoff(df, "09:50")
    assert result.loc[0, "generation"] == 70
