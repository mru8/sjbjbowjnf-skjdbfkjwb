import pandas as pd

def select_forecast_at_cutoff(forecasts, cutoff_time = "09:50"):
    """For each delivery hour, keep the latest forecast published at or before the 
    cutoff_time on the day before the delivery day.
    
    forecasts needs the columns publishTime, startTime and generation,
    with the two times as UTC timestamps. Hours with no allowed forecast
    are left out of the result, so they show up as gaps.
    Assumes UTC equals UK time (true in winter)."""

    hours, minutes = map(int, cutoff_time.split(":"))
    df = forecasts.copy()

    delivery_day = df["startTime"].dt.normalize()
    df["cutoff"] = (
        delivery_day - pd.Timedelta(days=1) + pd.Timedelta(hours=hours, minutes=minutes)
    )

    allowed = df[df["publishTime"] <= df["cutoff"]]
    latest = allowed.sort_values(["startTime", "publishTime"]).drop_duplicates(
        "startTime", keep="last"
    )
    return latest.reset_index(drop=True)