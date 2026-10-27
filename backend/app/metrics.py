import pandas as pd

def build_comparison(selected, hourly_actuals):
    """Line up each selected forecast with the actual for the same hour.
    
    selected: output of select_forecast_at_cutoff (startTime, publishTime, generation).
    hourly_actuals: output of to_hourly (startTime, actual).
    Only hours present in both are kept; nothing is filled in.
    error = forecast - actual, so a positive error means wind was over forecast.
    hours_ahead = how long before the target hour the forecast was published."""

    forecast = selected.rename(columns={"generation": "forecast"})[
        ["startTime", "publishTime", "forecast"]
    ]
    merged = forecast.merge(hourly_actuals, on="startTime", how="inner")
    merged["error"] = merged["forecast"] - merged["actual"]
    merged["abs_error"] = merged["error"].abs()
    merged["hours_ahead"] = (
        merged["startTime"] - merged["publishTime"]
    ).dt.total_seconds() / 3600
    return merged.sort_values("startTime").reset_index(drop=True)

def summarise(comparison):
    """Headline accuracy numbers, all in MW"""
    if comparison.empty:
        return {"n_hours": 0, "mae": None, "rmse": None, "bias": None, "p95_abs_error": None}

    error = comparison["error"]
    return {
        "n_hours": int(len(error)),
        "mae": float(error.abs().mean()),
        "rmse": float((error**2).mean()**0.5),
        "bias": float(error.mean()),
        "p95_abs_error": float(error.abs().quantile(0.95)),
    }