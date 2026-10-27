import pandas as pd

def to_hourly(actuals):
    """Average the two half-hour readings in each hour into one hourly MW value.
    
    actuals needs the columns startTime (UTC timestamps) and generation.
    An hour is kept only if both of its half-hours are present, so missing
    data shows up as a gap and is never filled in.
    Returns the columns startTime (hour start) and actual."""

    df = actuals.drop_duplicates("startTime", keep="last").copy()
    df["hour"] = df["startTime"].dt.floor("h")

    grouped = df.groupby("hour")["generation"].agg(["mean", "count"]).reset_index()
    complete = grouped[grouped["count"] == 2]

    return (
        complete.rename(columns={"hour": "startTime", "mean": "actual"})[
            ["startTime", "actual"]
        ]
        .sort_values("startTime")
        .reset_index(drop=True)
    )