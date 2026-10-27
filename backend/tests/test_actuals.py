import pandas as pd

from app.actuals import to_hourly

def make_actuals(rows):
    """rows: list of (startTime, generation)."""
    df = pd.DataFrame(rows, columns=["startTime", "generation"])
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
    return df

def test_two_half_hours_are_averaged():
    df = make_actuals([
        ("2026-01-15 12:00", 100),
        ("2026-01-15 12:30", 200),
    ])
    result = to_hourly(df)
    assert len(result) == 1
    assert result.loc[0, "actual"] == 150

def test_hour_with_only_one_half_hour_is_left_out():
    df = make_actuals([
        ("2026-01-15 12:00", 100),
    ])
    assert len(to_hourly(df)) == 0

def test_duplicate_half_hour_is_not_counted_twice():
    df = make_actuals([
        ("2026-01-15 12:00", 100),
        ("2026-01-15 12:00", 100) #same half hour twice, other half missing
    ])
    assert len(to_hourly(df)) == 0