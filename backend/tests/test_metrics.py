import pandas as pd
import pytest

from app.metrics import build_comparison, summarise

PUBLISHED = pd.Timestamp("2026-01-14 09:30", tz="UTC")

def comparison_from(pairs):
    """pairs: list of (forecast, actual), one per consecutive hour."""
    start = pd.Timestamp("2026-01-15 00:00", tz="UTC")
    forecasts, actuals = [], []
    for i, (f, a) in enumerate(pairs):
        t = start + pd.Timedelta(hours=i)
        forecasts.append({"startTime": t, "publishTime": PUBLISHED, "generation": f})
        actuals.append({"startTime": t, "actual": a})
    return build_comparison(pd.DataFrame(forecasts), pd.DataFrame(actuals))

def test_error_is_forecast_minus_actual():
    result = comparison_from([(110, 100)])
    assert result.loc[0, "error"] == 10

def test_bias_keeps_sign_and_mae_does_not():
    result = summarise(comparison_from([(110, 100), (70, 100)])) #errors +10, -30
    assert result["bias"] == -10
    assert result["mae"] == 20

def test_rmse_punishes_big_misses():
    result = summarise(comparison_from([(110, 100), (70, 100)]))
    assert result["rmse"] == pytest.approx(500**0.5)

def test_p95_absolute_error():
    pairs = [(100 + e, 100) for e in (10, 20, 30, 40, 50)]
    result = summarise(comparison_from(pairs))
    assert result["p95_abs_error"] == pytest.approx(48)

def test_hour_without_an_actual_is_left_out():
    t0 = pd.Timestamp("2026-01-15 00:00", tz="UTC")
    t1 = pd.Timestamp("2026-01-15 01:00", tz="UTC")
    forecasts = pd.DataFrame({
        "startTime": [t0, t1],
        "publishTime": [PUBLISHED, PUBLISHED],
        "generation": [100, 200],
    })
    actuals = pd.DataFrame({"startTime": [t0], "actual": [90]})
    result = build_comparison(forecasts, actuals)
    assert len(result) == 1

def test_summary_of_empty_comparison_has_no_numbers():
    result = summarise(pd.DataFrame({"error": []}))
    assert result["n_hours"] == 0
    assert result["mae"] is None
    assert result["p95_signed_error"] is None

def test_hours_ahead_is_publish_to_target_gap():
    forecasts = pd.DataFrame({
        "startTime": [pd.Timestamp("2026-01-15 12:00", tz="UTC")],
        "publishTime": [PUBLISHED],
        "generation": [100],
    })
    actuals = pd.DataFrame({
        "startTime": [pd.Timestamp("2026-01-15 12:00", tz="UTC")],
        "actual": [90],
    })
    result = build_comparison(forecasts, actuals)
    assert result.loc[0, "hours_ahead"] == 26.5

def test_p95_signed_error_keeps_direction():
    # errors -50, -20, +10, +20, +30
    pairs = [(100+e, 100) for e in (-50, -20, 10, 20, 30)]
    result = summarise(comparison_from(pairs))
    assert result["p95_signed_error"] == pytest.approx(28)
    assert result["p95_abs_error"] == pytest.approx(46)